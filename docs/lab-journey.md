# Lab Journey

This project is based on completing and extending the FSDL text recognizer labs.

## What Was Covered

1. PyTorch and baseline neural networks for image recognition.
2. CNN-based character recognition.
3. Transformer and sequence-to-sequence handwriting recognition.
4. Experiment tracking and model comparison.
5. Debugging and troubleshooting training/inference issues.
6. IAM data processing, Label Studio workflow, and IAMParagraphs preparation.
7. Deployment with Docker, AWS ECR, Lambda, and public endpoints.
8. Monitoring, logging, API behavior checks, and load testing.

## Extra Work Beyond Running Notebooks

- Repaired broken notebook bootstrap cells and dependency issues.
- Created Modal-ready notebook tooling for cloud execution experiments.
- Studied and documented OCR architecture progression from MLP to ResnetTransformer.
- Fetched and validated the pretrained IAMParagraphs TorchScript model.
- Built assignment-compliant `/health` and `/predict` APIs using multipart image upload.
- Deployed the model as a Lambda Function URL backed by ECR.
- Created a minimal UI for live image upload and prediction.
- Load-tested the deployed endpoint with Locust and documented bottlenecks.
