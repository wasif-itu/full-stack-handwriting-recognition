# Comprehensive Text Recognition Model Documentation

## Overview

This documentation provides **detailed explanations of 6 models** in the FSDL text recognizer curriculum, progressing from simple character classification to full paragraph OCR. Each model is documented with:

1. **Programming Implementation** - Exact layer specifications, learnable parameter counts
2. **Conceptual Structure** - Why each layer exists, what problem it solves
3. **Shape Transformations** - Input/output shapes with mathematical formulas
4. **Dataset Analysis** - Which dataset, why those dimensions, how data flows
5. **Why It's an Improvement** - Comparison to previous models
6. **Shortcomings** - Why we don't stop here, what the next model fixes
7. **Visual Diagrams** - LaTeX-rendered architecture diagrams

---

## Model Progression

### 1. 📄 **MLP + EMNIST** (`mlp_emnist.pdf`)
- **Task:** Single character classification (baseline)
- **Input:** 28×28 grayscale character images
- **Output:** Single class prediction (83 classes)
- **Parameters:** 945,739
- **Key Formula:** Linear transformation: $\mathbf{h} = Xᵀ W + \mathbb{b}$
- **Why:** Simplest possible approach for comparison
- **Shortcoming:** Treats image as flat vector, loses 2D spatial structure

### 2. 🧠 **CNN + EMNIST** (`cnn_emnist_enhanced.pdf`)
- **Task:** Single character classification with spatial awareness
- **Input:** 28×28 gayscale character (same as MLP)
- **Output:** Single class prediction (83 classes)
- **Parameters:** 1,654,035
- **Architecture:**
  - Conv1: 3×3, stride 1, padding 1 → (B, 64, 28, 28)
  - Conv2: 3×3, stride 1, padding 1 → (B, 64, 28, 28)  
  - MaxPool2×2: stride 2 → (B, 64, 14, 14)
  - FC: 12,544 → 128 → 83
- **Key Formula:** Convolution: $H_{out} = \lfloor \frac{H_{in} + 2p - k}{s} \rfloor + 1$
- **Why:** Convolution preserves 2D spatial structure, learns hierarchical features
- **Shortcoming:** Still only predicts 1 class per image—can't do sequences

### 3. 🪟 **LineCNNSimple + EMNIST Lines** (`linecnnsimple_emnistlines_detailed.pdf`)
- **Task:** Text line recognition with perfectly separated characters
- **Input:** Variable-width lines of concatenated EMNIST characters (B, 1, 28, W_var)
- **Output:** Sequence of character predictions (B, 83, S) where S = number of windows
- **Parameters:** 1,654,035 (same CNN reused for all windows)
- **Key Technique:** Sliding window with fixed 28×28 windows, stride 28
- **Window Calculation:** $S = \lfloor \frac{W - WW}{WS} \rfloor + 1$
- **Why:** Enables variable-length input, outputs character sequences
- **Shortcoming:** Assumes clean separation, each window independent (no context)

### 4. 🏗️ **LineCNN + IAM Lines** (`linecnn_iamlines_detailed.pdf`)
- **Task:** Real handwritten line OCR with cursive, overlapping text
- **Input:** 56×1536 real handwritten text lines
- **Output:** Sequence of character logits (B, 83, S_x) where S_x ≈ 48
- **Parameters:** 1,199,140
- **Architecture:** 9 convolutional blocks with 3 stride-2 downsampling:
  - Initial: 56×1536 → Conv1 (stride 1) → 56×1536
  - Downsample 1: stride 2 → 28×768
  - Downsample 2: stride 2 → 14×384 (with channel expansion 32→64)
  - Downsample 3: stride 2 → 7×192 (with channel expansion 64→128)
  - **Crucial:** Final depthwise conv (7, 2) kernel flattens spatial dims → (1, S_x)
  - FC layers: 512 → 512 → 83
- **Key Formula:** After 3 stride-2 layer: width reduced 2³ = ×8
- **Why:** Hierarchical multiscale learning, implicit sliding, handles real handwriting
- **Shortcoming:** No language model—predicts each character independently

### 5. 🤖 **LineCNNTransformer + IAM Lines** (`linecnntransformer_iamlines_detailed.pdf`)
- **Task:** Same as LineCNN but with language context
- **Input:** 56×1536 real handwritten text lines
- **Output:** Autoregressive character sequence
- **Parameters:** 3,340,919
  - Encoder (LineCNN): 1,199,140
  - Transformer embedding: 21,248
  - Transformer decoder (4 layers): 2,099,200
  - Output projection: 21,331
- **Key Components:**
  - **Encoder:** Uses LineCNN to extract image features $(B, 256, S_x)$ → $(S_x, B, 256)$
  - **Positional Encoding:** $PE(i, 2j) = \sin(i/10000^{2j/D}), PE(i, 2j+1) = \cos(i/10000^{2j/D})$
  - **Decoder:** Transformer with causal mask to prevent attending to future tokens
  - **Causal Mask:** Prevents position $i$ from attending to position $j$ where $j > i$
- **Why:** Transformer decoder provides context—previous tokens help predict current one
- **Shortcoming:** Autoregressive inference is SLOW (×50 slower than LineCNN)

### 6. 📚 **ResnetTransformer + IAM Paragraphs** (`resnettransformer_iamparagraphs_detailed.pdf`)
- **Task:** Full paragraph OCR with multi-line layout
- **Input:** 576×640 full paragraph images (multiple lines of text)
- **Output:** Autoregressive sequence up to 682 characters (includes newline token)
- **Parameters:** 15,679,796 (11.2M for ResNet-18 + 4.5M trainable)
- **Architecture:**
  - **Encoder:** ResNet-18 backbone (pre-trained):
    - Input 576×640 → Conv1 (stride 2) → 288×320
    - Max pool (stride 2) → 144×160
    - ResNet blocks with intra-block strides → final: 18×20 (×32 downsampling)
    - Output: (B, 512, 18, 20) → Projection to (B, 256, 18, 20)
  - **2D Positional Encoding:** $PE_{2D}(h, w, d) = \sin(h/10000^{d/D}) + \cos(w/10000^{d/D})$
  - **Flattening:** 18×20 spatial grid → 360 sequence elements
  - **Decoder:** Transformer (4 layers) with 84 tokens (83 chars + newline)
- **Key Formula:** ResNet spatial reduction: $576 \to 288 \to 144 \to 72 \to 36 \to 18$ (each stage ÷2)
- **Why:** 
  - 2D layout handled naturally (not just 1D sequences)
  - Pre-trained ResNet features from ImageNet
  - Deeper network (18 layers) captures complex patterns
  - Skip connections enable optimization in deep nets
- **Shortcoming:** Expensive (60MB), slow inference (1-5s per page), requires GPU

---

## Quick Comparison Table

| Model | Parameters | Size | Speed | Max Input | Dataset | Accuracy |
|-------|-----------|------|-------|-----------|---------|----------|
| **MLP** | 0.95M | 3.6MB | 1000+ Hz | 28×28 | EMNIST | ~82% |
| **CNN** | 1.65M | 6.3MB | 500+ Hz | 28×28 | EMNIST | ~94% |
| **LineCNNSimple** | 1.65M | 6.3MB | 400+ Hz | 28×W_var | EMNIST-L | ~89% |
| **LineCNN** | 1.20M | 4.6MB | 300+ Hz | 56×1536 | IAM-L | ~93% |
| **LineCNNTransformer** | 3.34M | 12.8MB | 5-10 Hz | 56×1536 | IAM-L | ~96% |
| **ResnetTransformer** | 15.68M | 60MB | 1-2 Hz | 576×640 | IAM-P | ~92% |

---

## Key Mathematical Concepts

### 1. Convolution Output Shape Formula
$$H_{out} = \left\lfloor \frac{H_{in} + 2 \cdot \text{padding} - \text{kernel}}{stride} \right\rfloor + 1$$

**Example:** 28×28 input, 3×3 kernel, padding 1, stride 1
$$H_{out} = \left\lfloor \frac{28 + 2 - 3}{1} \right\rfloor + 1 = 28$$

### 2. Parameter Count (Linear Layers)
$$\text{Parameters} = \text{in\_features} \times \text{out\_features} + \text{out\_features}$$
(The extra term is the bias vector)

**Example:** Linear(1024 → 128)
$$\text{Params} = 1024 \times 128 + 128 = 131{,}200$$

### 3. Parameter Count (Convolutional Layers)
$$\text{Parameters} = \text{in\_channels} \times \text{out\_channels} \times k_h \times k_w + \text{out\_channels}$$

**Example:** Conv2d(64 in, 64 out, 3×3 kernel)
$$\text{Params} = 64 \times 64 \times 3 \times 3 + 64 = 36{,}928$$

### 4. Positional Encoding (1D - Transformer)
$$PE(pos, 2i) = \sin\left(\frac{pos}{10000^{2i/d_{\text{model}}}}\right)$$
$$PE(pos, 2i+1) = \cos\left(\frac{pos}{10000^{2i/d_{\text{model}}}}\right)$$

**Purpose:** Give transformer information about sequence order

### 5. Causal Attention Mask
- Position $i$ can attend to positions $[0, 1, \ldots, i]$ (past + current)
- Position $i$ **cannot** attend to positions $[i+1, \ldots, S]$ (future)
- Implemented as: $\text{mask}[i,j] = -\infty$ if $j > i$, else $0$

**Purpose:** Enable autoregressive generation (generating one token at a time)

---

## Dataset Summary

### EMNIST (Elementary MNIST)
- **Source:** NIST Special Database 19
- **Size:** 814,255 samples
- **Classes:** 62 (digits 0-9, uppercase A-Z, lowercase a-z)
- **Dimensions:** 28×28 pixels
- **Format:** Grayscale, 8-bit intensity (0-255)
- **Use:** Character-level recognition, baseline models

### EMNIST Lines (Synthetic)
- **Source:** Concatenated EMNIST characters
- **Size:** Generated on-the-fly from EMNIST
- **Dimensions:** Variable width × 28 pixels height
- **Format:** Perfectly separated characters
- **Use:** Transition from single-char to sequence models

### IAM Lines (Real Handwriting)
- **Source:** IAM Handwriting Database at ICDAR 1999
- **Size:** 9,862 text lines
- **Dimensions:** 56×1536 pixels (downsampled 2×)
- **Format:** Real cursive handwriting, variable script
- **Use:** Line-level text recognition

### IAM Paragraphs (Full Documents)
- **Source:** IAM Database, grouped into paragraphs
- **Dimensions:** 576×640 pixels per image
- **Format:** Multi-line text, natural layout
- **Max sequence:** 682 characters (including newlines)
- **Use:** Full-page OCR, document processing

---

## Why Each Model is an Improvement

| From | To | Key Improvement |
|------|----|----|
| MLP | CNN | **Inductive bias:** 2D convolution preserves spatial locality → better features |
| CNN | LineCNNSimple | **Variable length:** Sliding window enables sequences → can process lines |
| LineCNNSimple | LineCNN | **Multiscale:** Strided convolutions learn hierarchical features → handles real data |
| LineCNN | LineCNNTransformer | **Context:** Transformer decoder sees previous tokens → can correct errors |
| LineCNNTransformer | ResnetTransformer | **2D layout:** ResNet handles 2D images naturally + pre-trained features |

---

## Implementation Pattern

All models follow this pattern in Python:

```python
class MyModel(nn.Module):
    def __init__(self, data_config, args=None):
        super().__init__()
        # Build layers
        
    def forward(self, x):
        # Pass through layers
        return output
        
    @staticmethod
    def add_to_argparse(parser):
        # Add hyperparameters
        return parser
```

Each model has:
- **Input validation:** Check dimensions match expected
- **Parameter logging:** Know exact layer sizes
- **Forward hooks:** For debugging tensor shapes

---

## Generated Files

### LaTeX PDFs (in `/lab06/latex/`)
1. **mlp_emnist.pdf** - MLP baseline model
2. **cnn_emnist_enhanced.pdf** - CNN with detailed formulas
3. **linecnnsimple_emnistlines_detailed.pdf** - Simple sliding window approach
4. **linecnn_iamlines_detailed.pdf** - Advanced CNN with strides (most in-depth)
5. **linecnntransformer_iamlines_detailed.pdf** - Encoder-decoder with transformer
6. **resnettransformer_iamparagraphs_detailed.pdf** - State-of-art ResNet+Transformer
7. **model_progression_summary.pdf** - Quick reference comparing all 6 models

### Source Files (in `/lab06/latex/`)
- `*_detailed.tex` - LaTeX source (edit, recompile with `latexmk -pdf FILE.tex`)
- `diagram_preamble.tex` - Shared formatting (colors, commands)

---

## How to Use This Documentation

### For Beginners:
1. Start with **model_progression_summary.pdf** for big picture
2. Read **mlp_emnist.pdf** to understand parameters and layer counting
3. Read **cnn_emnist_enhanced.pdf** to see how convolution works

### For Implementation:
1. Look at shape evolution tables in each PDF
2. Verify parameter counts by hand: $\text{in} \times \text{out} + \text{bias}$
3. Cross-reference with source code in `/lab06/text_recognizer/models/`

### For Optimization:
1. See parameter counts and model sizes (top right of each PDF)
2. Refer to datasets summary to understand input constraints
3. Use shortcomings to understand where next model improves

### For Teaching:
- **Use individual PDFs** for lectures (one model per class)
- **Use summary PDF** for high-level overview
- **Point out comparisons** between models (see comparison tables in each PDF)

---

## Common Formulas Reference

### Convolution Details
- **1D Conv:** Single time sequence (rare in vision)
- **2D Conv:** Images (height × width)
- **Groups:** Depthwise convolution when groups = input_channels

### Pooling
- **MaxPool:** $\text{output} = \max(\text{window})$ - reduces spatial resolution
- **AvgPool:** $\text{output} = \text{mean}(\text{window})$ - smoother alternative

### Normalization
- **Batch Norm:** $\text{output} = \gamma \cdot \frac{x - \text{mean}}{\sqrt{\text{var} + \epsilon}} + \beta$
- **Layer Norm:** Same as batch norm but over features, not batch

### Activation Functions
- **ReLU:** $\text{ReLU}(x) = \max(0, x)$ - non-linearity, no learnable params
- **Softmax:** $\text{softmax}(x)_i = \frac{e^{x_i}}{\sum_j e^{x_j}}$ - converts logits to probabilities

### Cross-Entropy Loss
$$\mathcal{L} = -\sum_{c=1}^{C} Y_c \log(\text{softmax}(\mathbf{z})_c)$$
where $Y$ is one-hot ground truth, $\mathbf{z}$ is logits

---

## See Also

- **Source Code:** `/lab06/text_recognizer/models/` - Python implementations
- **Data Loading:** `/lab06/text_recognizer/data/` - Dataset classes
- **Training:** `/lab06/training/` - Experiment runners
- **Notebooks:** `/lab06/notebooks/` - Interactive tutorials

---

## Questions to Test Understanding

1. Why does CNN have better parameter efficiency than MLP for images?
2. What is the output shape of LineCNN when input is (2, 1, 56, 1536)?  
3. Why can't LineCNNSimple handle cursive handwriting well?
4. What is the purpose of the causal mask in the transformer decoder?
5. Why is ResNet better for paragraphs than a custom CNN?
6. How many parameters in a Conv2d(32→64, 3×3) layer?
7. What problem does positional encoding solve in transformers?

---

Generated: April 18, 2026  
LaTeX compilation: Successful (7/7 files)  
Total documentation: ~1.5MB of visual diagrams
