"""AWS Lambda API for the IAM paragraph text recognizer."""
import base64
import json
import os
from io import BytesIO
from pathlib import Path

from PIL import Image
from requests_toolbelt.multipart import decoder
import torch

from text_recognizer.paragraph_text_recognizer import ParagraphTextRecognizer


ROLL_NO = os.getenv("ROLL_NO", "BSCS23020")
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
JSON_HEADERS = {
    "content-type": "application/json",
    "access-control-allow-origin": "*",
    "access-control-allow-methods": "GET,POST,OPTIONS",
    "access-control-allow-headers": "content-type",
}

torch.set_num_threads(int(os.getenv("TORCH_NUM_THREADS", "2")))
_recognizer = None


def handler(event, _context):
    """Route Lambda Function URL requests to the required API endpoints."""
    method = _method(event)
    path = _path(event)

    if method == "OPTIONS":
        return _json_response({"ok": True})

    if method == "GET" and path == "/health":
        return _json_response({"status": "healthy", "roll_no": ROLL_NO})

    if method == "POST" and path == "/predict":
        try:
            image = _extract_uploaded_image(event)
            prediction = _get_recognizer().predict(image)
            return _json_response({"success": True, "prediction": prediction})
        except Exception as exc:
            print(f"ERROR invalid prediction request: {type(exc).__name__}: {exc}")
            return _json_response({"success": False, "error": "Invalid image"})

    return _json_response({"success": False, "error": "Not found"}, status_code=404)


def _get_recognizer():
    global _recognizer
    if _recognizer is None:
        print("INFO loading ParagraphTextRecognizer")
        _recognizer = ParagraphTextRecognizer()
        print("INFO ParagraphTextRecognizer loaded")
    return _recognizer


def _method(event):
    return (
        event.get("requestContext", {})
        .get("http", {})
        .get("method", event.get("httpMethod", ""))
        .upper()
    )


def _path(event):
    raw_path = event.get("rawPath") or event.get("path") or "/"
    return raw_path.rstrip("/") or "/"


def _extract_uploaded_image(event):
    content_type = _header(event, "content-type")
    if not content_type or "multipart/form-data" not in content_type:
        raise ValueError("request is not multipart/form-data")

    body = event.get("body")
    if body is None:
        raise ValueError("missing body")

    body_bytes = base64.b64decode(body) if event.get("isBase64Encoded") else body.encode()
    multipart_data = decoder.MultipartDecoder(body_bytes, content_type)

    for part in multipart_data.parts:
        disposition = part.headers.get(b"Content-Disposition", b"").decode()
        if 'name="image"' not in disposition:
            continue
        filename = _filename_from_disposition(disposition)
        if not _has_supported_extension(filename):
            raise ValueError(f"unsupported image extension: {filename}")
        return _image_from_bytes(part.content)

    raise ValueError("missing image field")


def _image_from_bytes(image_bytes):
    with Image.open(BytesIO(image_bytes)) as image:
        image.load()
        return image.convert("L")


def _header(event, name):
    headers = event.get("headers") or {}
    lowered = {key.lower(): value for key, value in headers.items()}
    return lowered.get(name.lower())


def _filename_from_disposition(disposition):
    for item in disposition.split(";"):
        item = item.strip()
        if item.startswith("filename="):
            return item.split("=", 1)[1].strip('"')
    return ""


def _has_supported_extension(filename):
    return Path(filename).suffix.lower() in SUPPORTED_EXTENSIONS


def _json_response(payload, status_code=200):
    return {
        "statusCode": status_code,
        "headers": JSON_HEADERS,
        "body": json.dumps(payload),
    }
