# Text Recognizer Lambda

AWS Lambda + ECR deployment for the pretrained FSDL IAM paragraph text recognizer.

## Public API

Base URL:

```text
https://ajqmhubrppdy65qq5hkbqxkfme0evvni.lambda-url.us-east-1.on.aws/
```

## Endpoints

### Health

```http
GET /health
```

Expected response:

```json
{"status": "healthy", "roll_no": "BSCS23020"}
```

Test:

```bash
curl https://ajqmhubrppdy65qq5hkbqxkfme0evvni.lambda-url.us-east-1.on.aws/health
```

### Predict

```http
POST /predict
```

Input:

```text
Content-Type: multipart/form-data
field name: image
supported files: .png, .jpg, .jpeg
```

Success response:

```json
{"success": true, "prediction": "recognized handwritten text"}
```

Error response:

```json
{"success": false, "error": "Invalid image"}
```

Test with the bundled IAM paragraph image:

```bash
curl -X POST \
  -F "image=@text_recognizer/tests/support/paragraphs/a01-077.png;type=image/png" \
  https://ajqmhubrppdy65qq5hkbqxkfme0evvni.lambda-url.us-east-1.on.aws/predict
```

Or run the Python test client:

```bash
/home/wasif/miniconda3/envs/fsdl-text-recognizer-2022/bin/python test_predict_api.py \
  https://ajqmhubrppdy65qq5hkbqxkfme0evvni.lambda-url.us-east-1.on.aws/
```

## Model

The deployment uses the pretrained FSDL IAM paragraph recognizer:

```text
text_recognizer/artifacts/paragraph-text-recognizer/model.pt
```

This is a TorchScript `ResnetTransformer` model trained for `IAMParagraphs`.

## Local UI

A minimal browser UI is available at:

```text
ui/index.html
```

Start it locally:

```bash
cd ui
python serve.py
```

Then open:

```text
http://127.0.0.1:8088/index.html
```

## Deployment

Deploy or redeploy:

```bash
bash deploy.sh
```

Current Lambda settings:

```text
function name: text-recognizer-api-bscs23020
memory: 3008 MB
timeout: 300 seconds
region: us-east-1
```

## Notes

The API satisfies the assignment requirements:

- public HTTPS endpoint
- `GET /health`
- `POST /predict`
- multipart upload using field name `image`
- JSON responses only
- plain-text prediction output
- `.png`, `.jpg`, and `.jpeg` support

Cold starts are slow because Lambda has to load PyTorch and the 416 MB model. A cold `/predict` can take around 2 minutes. Warm predictions are much faster.
