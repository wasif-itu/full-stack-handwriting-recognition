# Architecture Study

This project studies handwriting recognition architectures from simple image classifiers to paragraph-level OCR models.

## Progression

- MLP on MNIST: baseline dense network for simple digits.
- CNN on EMNIST: spatial feature extraction for character images.
- LineCNN and LineCNNSimple: convolutional sequence models for line-level text.
- LineCNNTransformer: CNN encoder with Transformer decoding for IAM line recognition.
- ResnetTransformer: ResNet-18 visual encoder with Transformer decoder for IAM paragraph recognition.

## Main Learned Idea

OCR becomes harder as the input moves from single characters to full paragraphs. The model must preserve spatial layout, represent long text sequences, and decode characters autoregressively. The ResnetTransformer handles this by converting the paragraph image into a 2D feature map and decoding text with a Transformer.
