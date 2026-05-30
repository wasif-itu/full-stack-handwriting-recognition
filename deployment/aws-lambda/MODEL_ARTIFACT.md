# Model Artifact

The deployed model is the pretrained FSDL IAM paragraph recognizer:

```text
text_recognizer/artifacts/paragraph-text-recognizer/model.pt
```

It is a TorchScript ResnetTransformer model for IAMParagraphs and is approximately 416 MB, so it is intentionally not committed to this Git repository.

In the original lab workspace, it was fetched/staged via the FSDL W&B artifact flow and placed under:

```text
lab08/text_recognizer/artifacts/paragraph-text-recognizer/model.pt
```

Before building the Docker image, place the model at:

```text
deployment/aws-lambda/text_recognizer/artifacts/paragraph-text-recognizer/model.pt
```
