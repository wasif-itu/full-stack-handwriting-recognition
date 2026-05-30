import base64
import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))
import api  # noqa: E402


def make_event(image_path):
    image_bytes = Path(image_path).read_bytes()
    boundary = "----textrecognizerboundary"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="{Path(image_path).name}"\r\n'
        "Content-Type: image/png\r\n\r\n"
    ).encode() + image_bytes + f"\r\n--{boundary}--\r\n".encode()
    return {
        "rawPath": "/predict",
        "requestContext": {"http": {"method": "POST"}},
        "headers": {"content-type": f"multipart/form-data; boundary={boundary}"},
        "isBase64Encoded": True,
        "body": base64.b64encode(body).decode(),
    }


def test_health():
    event = {"rawPath": "/health", "requestContext": {"http": {"method": "GET"}}}
    response = api.handler(event, None)
    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == {"status": "healthy", "roll_no": "BSCS23020"}


def test_predict_support_image():
    image_path = Path("text_recognizer/tests/support/paragraphs/a01-077.png")
    response = api.handler(make_event(image_path), None)
    payload = json.loads(response["body"])
    assert response["statusCode"] == 200
    assert payload["success"] is True
    assert "West" in payload["prediction"]
