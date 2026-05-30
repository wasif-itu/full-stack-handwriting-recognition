# Full-Stack Handwriting Recognition System

End-to-end handwriting OCR project covering model architecture study, IAM data preparation, ResNet-Transformer inference, AWS Lambda deployment, a minimal browser UI, and Locust load testing.

This work is based on the FSDL text recognizer labs and extends them into a portfolio-ready deployment and evaluation project.

## Highlights

- Studied OCR architecture progression from MLP/CNN baselines to Transformer-based sequence models.
- Documented IAM line and paragraph recognition pipelines.
- Validated a pretrained IAMParagraphs ResnetTransformer TorchScript model.
- Built an assignment-compliant public API with `GET /health` and `POST /predict`.
- Deployed the model using Docker, AWS ECR, and AWS Lambda Function URLs.
- Added a minimal local UI for uploading images and viewing predictions.
- Performed Locust load testing and documented latency bottlenecks.

## Live API

Base URL:

```text
https://ajqmhubrppdy65qq5hkbqxkfme0evvni.lambda-url.us-east-1.on.aws/
```

Health check:

```bash
curl https://ajqmhubrppdy65qq5hkbqxkfme0evvni.lambda-url.us-east-1.on.aws/health
```

Prediction:

```bash
curl -X POST \
  -F "image=@deployment/aws-lambda/text_recognizer/tests/support/paragraphs/a01-077.png;type=image/png" \
  https://ajqmhubrppdy65qq5hkbqxkfme0evvni.lambda-url.us-east-1.on.aws/predict
```

## Architecture

```text
Image upload
    -> Lambda Function URL
    -> Docker image from ECR
    -> multipart parser
    -> ParagraphTextRecognizer
    -> TorchScript ResnetTransformer model
    -> JSON prediction response
```

The OCR model uses a ResNet encoder to extract spatial visual features and a Transformer decoder to generate text autoregressively.

## Repository Structure

```text
docs/                 Architecture notes and lab journey
diagrams/             Model and data pipeline diagrams
deployment/aws-lambda AWS Lambda container deployment code
deployment/ui         Minimal browser UI for live testing
load-testing/         Locust script, report, and CSV results
proof/                Generated proof artifacts such as Locust HTML report
tools/                Modal notebook runner and helper scripts
```

## Model Artifact

The pretrained model is not committed because it is large:

```text
text_recognizer/artifacts/paragraph-text-recognizer/model.pt
```

It is a TorchScript IAMParagraphs ResnetTransformer model, approximately 416 MB. See `deployment/aws-lambda/MODEL_ARTIFACT.md` for placement details.

## Load Test Summary

Final Locust run:

```text
Users: 10
Spawn Rate: 2
Duration: 60 seconds
Total Requests: 52
Total Failures: 0
Average Response Time: 9096.11 ms
95th Percentile: 12000 ms
Conclusion: STABLE
```

See `load-testing/bscs23020_lt_mlops.txt` and `proof/locust_report.html`.

## Important Deployment Note

AWS Lambda cold starts are slow for this model because the container loads PyTorch and a large TorchScript model. Warm predictions are much faster, but the first prediction after idle time can take around two minutes.

## Resume Summary

Full-stack handwriting recognition system using PyTorch, TorchScript, ResnetTransformer OCR, Docker, AWS ECR, AWS Lambda, and Locust load testing.
