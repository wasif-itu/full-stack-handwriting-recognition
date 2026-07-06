# Full-Stack Handwriting Recognition System

End-to-end handwriting OCR project covering model architecture study, IAM data preparation, ResNet-Transformer inference, AWS Lambda deployment, a minimal browser UI, and Locust load testing.

## Highlights

- Studied OCR architecture progression from MLP/CNN baselines to Transformer-based sequence models.
- Documented IAM line and paragraph recognition pipelines.
- Validated a pretrained IAMParagraphs ResnetTransformer TorchScript model.
- Built an assignment-compliant public API with `GET /health` and `POST /predict`.
- Deployed the model using Docker, AWS ECR, and AWS Lambda Function URLs.
- Added a mobile-friendly Vercel-ready UI for camera capture, image upload, and prediction display.
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
deployment/ui         Browser UI for live testing and Vercel deployment
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

## Frontend Deployment

The frontend is a static app that can be deployed on Vercel. It lets users take
a photo on mobile or upload an image, compresses large phone photos in the
browser, normalizes bright paper images to the model's expected dark-background
polarity, sends the image to `/predict`, and displays the recognized text.

```bash
npm run build
vercel
```

Vercel reads `vercel.json`, builds `deployment/ui` into `dist/`, and serves the
app from there. For local testing:

```bash
npm start
```

## Resume Summary

Full-stack handwriting recognition system using PyTorch, TorchScript, ResnetTransformer OCR, Docker, AWS ECR, AWS Lambda, and Locust load testing.
