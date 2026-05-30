# Model Architecture Cheat Sheet

## 1. MLP (Multi-Layer Perceptron) + EMNIST

```
INPUT (B, 1, 28, 28) EMNIST grayscale image
  |
  v
FLATTEN to (B, 784)
  |
  v
FC LAYER: 784 → 1024
  Params: 784 × 1024 + 1024 = 803,840
  |
  v
ReLU
  |
  v
DROPOUT (p=0.5)
  |
  v
FC LAYER: 1024 → 128
  Params: 1024 × 128 + 128 = 131,200
  |
  v
ReLU
  |
  v
DROPOUT (p=0.5)
  |
  v
FC LAYER: 128 → 83
  Params: 128 × 83 + 83 = 10,699
  |
  v
OUTPUT (B, 83) logits
  
TOTAL PARAMS: 945,739
```

---

## 2. CNN (Convolutional NN) + EMNIST

```
INPUT (B, 1, 28, 28)
  |
  v
CONV2D(1→64): 3×3, stride=1, padding=1
  Output: (B, 64, 28, 28)
  Formula: (28 + 2 - 3)/1 + 1 = 28
  Params: 1 × 3 × 3 × 64 + 64 = 640
  |
  v
ReLU
  |
  v
CONV2D(64→64): 3×3, stride=1, padding=1
  Output: (B, 64, 28, 28)
  Params: 64 × 3 × 3 × 64 + 64 = 36,928
  |
  v
ReLU
  |
  v
MAXPOOL 2×2, stride=2
  Output: (B, 64, 14, 14)
  Formula: (28 - 2)/2 + 1 = 14
  |
  v
DROPOUT (p=0.25)
  |
  v
FLATTEN to (B, 12,544)
  [Since 64 × 14 × 14 = 12,544]
  |
  v
FC(12544→128)
  Params: 12,544 × 128 + 128 = 1,605,760
  |
  v
ReLU
  |
  v
FC(128→83)
  Params: 128 × 83 + 83 = 10,707
  |
  v
OUTPUT (B, 83) logits

TOTAL PARAMS: 1,654,035
```

---

## 3. LineCNNSimple (Sliding Window) + EMNIST Lines

```
INPUT (B, 1, 28, W_variable)  ← Variable width!
  
For each window s in range(S):
  Extract window: X[:, :, :, s*28:(s*28+28)] → (B, 1, 28, 28)
    |
    v
  Pass through CNN (same as CNN model above)
    |
    v
  Get logits: (B, 83)
  
Stack all S windows: (B, 83, S)
  
Number of windows: S = floor((W - 28) / 28) + 1

OUTPUT (B, 83, S) sequence of character predictions

MODEL REUSES: Same CNN applied to each window
TOTAL PARAMS: 1,654,035 (unchanged)
```

---

## 4. LineCNN (Advanced) + IAM Lines

```
INPUT (B, 1, 56, 1536)  ← Real handwritten lines

BLOCK 1: CONV(1→32) 3×3, stride=1, padding=1
  Output: (B, 32, 56, 1536)
  Params: 320
  
BLOCK 2: CONV(32→32) 3×3, stride=1, padding=1
  Output: (B, 32, 56, 1536)
  Params: 9,248
  
BLOCK 3: CONV(32→32) 3×3, stride=2, padding=1  ← DOWNSAMPLE
  Output: (B, 32, 28, 768)
  [56→28, 1536→768]
  Params: 9,248
  
BLOCK 4: CONV(32→32) 3×3, stride=1, padding=1
  Output: (B, 32, 28, 768)
  Params: 9,248
  
BLOCK 5: CONV(32→64) 3×3, stride=2, padding=1  ← DOWNSAMPLE + EXPAND
  Output: (B, 64, 14, 384)
  [28→14, 768→384]
  Params: 18,496
  
BLOCK 6: CONV(64→64) 3×3, stride=1, padding=1
  Output: (B, 64, 14, 384)
  Params: 36,928
  
BLOCK 7: CONV(64→128) 3×3, stride=2, padding=1  ← DOWNSAMPLE + EXPAND
  Output: (B, 128, 7, 192)
  [14→7, 384→192]
  Params: 73,856
  
BLOCK 8: CONV(128→128) 3×3, stride=1, padding=1
  Output: (B, 128, 7, 192)
  Params: 147,584
  
BLOCK 9: CONV(128→512) kernel=(7,2), stride=(7,2), padding=0  ← KEY!
  Output: (B, 512, 1, S_x)
  [This completely collapses height, keeps width as sequence]
  Params: 589,056
  
SQUEEZE height dimension: (B, 512, 1, S_x) → (B, 512, S_x)
  
PERMUTE: (B, 512, S_x) → (B, S_x, 512)
  
FC(512→512)
  Applied to each of S_x positions
  Params: 262,656
  
ReLU + Dropout(0.2)
  
FC(512→83)
  Applied to each position
  Params: 42,499
  
OUTPUT (B, S_x, 83) sequence logits
  Permute to (B, 83, S_x) for loss

TOTAL PARAMS: 1,199,140
```

**Key insight:** Final conv (7,2) kernel acts as feature aggregation across height, creating sequence!

---

## 5. LineCNNTransformer + IAM Lines

```
INPUT (B, 1, 56, 1536)

ENCODER (LineCNN):
  [Same as LineCNN above]
  Output: (B, 256, S_x) where S_x ≈ 48
  |
  v
  Scale by √256 = 16
  |
  v
  Add positional encodings
  |
  v
  Permute to (S_x, B, 256)
  |
  v
  MEMORY for decoder

DECODER:

Train-time forward:
  INPUT TOKENS Y_train: (B, S_y)
    |
    v
  EMBEDDING(83→256): (S_y, B, 256)
    |
    v
  Scale by √256 = 16
    |
    v
  Add positional encodings
    |
    v
  Create causal mask (S_y, S_y):
    mask[i,j] = -∞ if j > i else 0
    (prevents attending to future)
    |
    v
  Create padding mask:
    mask[b,t] = (Y[b,t] == PAD_TOKEN)
    |
    v
  TransformerDecoder(4 layers):
    - Self-attention with causal mask
    - Cross-attention to MEMORY
    - Feed-forward (256→1024→256)
    |
    v
  Output: (S_y, B, 256)
    |
    v
  FC(256→83): (S_y, B, 83)
    |
    v
  LOSS: CrossEntropy(logits, Y_train)

Test-time forward (autoregressive):
  Initialize: y[0] = START_TOKEN
  For t = 1 to max_len:
    y_input = y[0:t]  # All previous tokens
    logits = decoder(MEMORY, y_input)
    y[t] = argmax(logits[-1, :])
    if y[t] == END_TOKEN: break

TOTAL PARAMS: 3,340,919
  - LineCNN: 1,199,140
  - Embedding: 21,248
  - Transformer: 2,099,200
  - Output: 21,331
```

---

## 6. ResnetTransformer + IAM Paragraphs

```
INPUT (B, 1, 576, 640)  ← Full paragraph! Or (B, 3, 576, 640)

If single-channel: repeat to 3 channels for ResNet

ENCODER (ResNet-18):

Conv1: 3×3, stride=2
  (B, 3, 576, 640) → (B, 64, 288, 320)
  
MaxPool 3×3, stride=2
  (B, 64, 288, 320) → (B, 64, 144, 160)
  
ResBlock Group 1 (4 blocks), stride=1
  (B, 64, 144, 160) → (B, 64, 144, 160)
  
ResBlock Group 2 (2 blocks), stride=2
  (B, 64, 144, 160) → (B, 128, 72, 80)
  
ResBlock Group 3 (2 blocks), stride=2
  (B, 128, 72, 80) → (B, 256, 36, 40)
  
ResBlock Group 4 (2 blocks), stride=2
  (B, 256, 36, 40) → (B, 512, 18, 20)
  
[Normal ResNet ends here with AvgPool + FC, but we remove those]

OUTPUT of ResNet: (B, 512, 18, 20)

PROJECTION: CONV(512→256, 1×1)
  (B, 512, 18, 20) → (B, 256, 18, 20)
  
ADD POSITIONAL ENCODING 2D:
  PE_2D(h, w, d) = sin(h/10000^(d/D)) + cos(w/10000^(d/D))
  
FLATTEN spatial to sequence:
  (B, 256, 18, 20) → (B, 256, 360)
  [Since 18 × 20 = 360]
  
PERMUTE: (B, 256, 360) → (360, B, 256)
  
MEMORY for decoder

DECODER (same as LineCNNTransformer):

EMBEDDING(84→256):  ← 84 includes newline token
  (S_y, B, 256)
  
Scale by √256
  
Add positional encodings (1D, different from encoder)
  
Create causal mask + padding mask
  
TransformerDecoder(4 layers):
  d_model=256, nhead=4, dim_feedforward=1024
  
FC(256→84)
  
OUTPUT: Sequence of length up to 682

TOTAL PARAMS: 15,679,796
  - ResNet-18: 11,180,000 (pre-trained)
  - Projection: 131,328
  - Embedding: 21,504
  - Transformer: 4,325,376
  - Output: 21,588
```

---

## Parameter Count Formulas

### Linear Layer
```python
# in_features → out_features
params = in_features × out_features + out_features
         └─ weights ─────────────┘   └─ bias ─┘
```

### Conv2d Layer
```python
# (in_channels, out_channels, kernel_h, kernel_w)
params = in_channels × out_channels × kernel_h × kernel_w + out_channels
         └────────── weights ──────────────────────────┘   └─ bias ─┘
```

### Conv2d Example
```python
Conv2d(64, 128, 3, 3)
= 64 × 128 × 3 × 3 + 128
= 73,856 params
```

### Embedding Layer
```python
# (num_embeddings, embedding_dim)
params = num_embeddings × embedding_dim
```

---

## Shape Evolution Patterns

### Pattern 1: Preserve spatial (stride=1, padding=same)
```
(B, C, H, W) → Conv(stride=1, padding=1) → (B, C_out, H, W)
```

### Pattern 2: Downsample by 2 (stride=2)
```
(B, C, H, W) → Conv(stride=2, padding=1) → (B, C_out, H/2, W/2)
```

### Pattern 3: Depthwise aggregation (k=(H, W))
```
(B, C, H, W) → Conv(k=(H, W), stride=(H, W), padding=0) → (B, C_out, 1, 1)
[Collapses spatial dimensions completely]
```

### Pattern 4: Flatten to sequence
```
(B, C, H, W) → Flatten(start_dim=2) → (B, C, H*W)
(B, C, H*W) → Permute(0, 2, 1) → (B, H*W, C) for transformer
```

---

## Transformer Decoder Details

### Multi-Head Attention
```
Q, K, V come from:
- Q: previous tokens (current position attention)
- K, V: previous tokens (self-attention) OR encoder output (cross-attention)

Output = Attention(Q, K, V) = softmax(QK^T / √d_k) V

With causal mask: mask[i,j] = -∞ if j > i
This prevents position i from "looking at" future positions j
```

### Feed-Forward Network
```
FFN(x) = max(0, xW_1 + b_1) W_2 + b_2
         └─ ReLU ─┘  └─ Linear ─┘

In most transformers:
- x dimension: d_model = 256
- Hidden dimension: 4 × d_model = 1024 (or user-specified)
```

### LayerNorm + Residual
```
Each sub-layer: output = LayerNorm(x + SubLayer(x))
                           └─ residual connection ─┘

Prevents gradient vanishing in deep networks
```

---

## Dataset Dimensions Summary

| Dataset | Height | Width | # Samples | Classes | Use |
|---------|--------|-------|-----------|---------|-----|
| EMNIST | 28 | 28 | 814K | 62 | Single char |
| EMNIST-L | 28 | Variable | Generated | 62 | Text lines (synthetic) |
| IAM Lines | 56 | 1536 (max) | 9,862 | 83 | Real handwritten lines |
| IAM Paragraphs | 576 | 640 | 1,000+ | 84* | Full pages |

*Including newline token

---

## Common Mistakes & How to Avoid Them

### 1. Wrong parameter count
❌ `params = kernel_h × kernel_w × out_channels`  
✅ `params = in_channels × out_channels × kernel_h × kernel_w + out_channels`

### 2. Forgetting bias terms
❌ `params = 1024 × 128`  
✅ `params = 1024 × 128 + 128`  (bias!)

### 3. Using wrong formula for output shape
❌ `output_h = H_in / stride`  
✅ `output_h = ⌊(H_in + 2p - k) / s⌋ + 1`

### 4. Confusing permutation  
❌ `(B, C, H, W) → (C, H, W, B)` — loses batch structure!  
✅ `(B, C, H, W) → (B, H*W, C)` — preserves batching

### 5. Transformer not attending to past
❌ Creating mask then forgetting to apply it  
✅ Pass mask to attention: `attention(..., attn_mask=mask)`

### 6. Input dimensions not matching model
❌ Feeding 28×28 to a model expecting 56×1536  
✅ Resize or crop to expected dimensions

---

## Quick Reference: Which Model When?

| If your data is... | Use this model |
|-------------------|--|
| Single 28×28 characters | CNN + EMNIST |
| Single 28×28 but need accuracy | MLP if fast, CNN if accurate |
| Lines with perfect char separation | LineCNNSimple |
| Real handwritten lines, single line | LineCNN |
| Real handwritten lines, needs correction | LineCNNTransformer |
| Full paragraphs, multi-line layout | ResnetTransformer |
| Must be <5MB model | LineCNN |
| Don't have GPU available | CNN or LineCNN |
| Have GPU and need best accuracy | ResnetTransformer |

---

## See the LaTeX PDFs For:

✓ **Detailed explanations** of why each layer exists  
✓ **Full shape evolution** tables  
✓ **Complete parameter breakdown** for each layer  
✓ **Why** each model improves on previous  
✓ **Shortcomings** of each model  
✓ **When to use** each model  
✓ **Beautiful formatted diagrams**  

→ **PDF files in `/lab06/latex/`**

Generated: April 18, 2026
