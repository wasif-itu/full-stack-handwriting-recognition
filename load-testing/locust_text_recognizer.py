"""Locust load test for the deployed text recognizer Lambda API."""
from collections import Counter
import json
from pathlib import Path

from locust import HttpUser, constant, events, task


IMAGE_PATH = Path(__file__).resolve().parent / "text_recognizer_lambda" / "text_recognizer" / "tests" / "support" / "paragraphs" / "a01-077.png"
IMAGE_BYTES = IMAGE_PATH.read_bytes()
STATUS_CODES = Counter()
STATUS_OUTPUT = Path(__file__).resolve().parent / "load_testing_outputs" / "status_codes.json"


class TextRecognizerUser(HttpUser):
    wait_time = constant(1)

    @task
    def predict(self):
        files = {"image": (IMAGE_PATH.name, IMAGE_BYTES, "image/png")}
        with self.client.post("/predict", files=files, timeout=300, catch_response=True, name="/predict") as response:
            try:
                payload = response.json()
            except Exception as exc:
                response.failure(f"non-JSON response: {exc}")
                return

            if response.status_code != 200:
                response.failure(f"unexpected status {response.status_code}: {payload}")
            elif payload.get("success") is not True:
                response.failure(f"prediction failed: {payload}")
            elif not isinstance(payload.get("prediction"), str) or not payload["prediction"].strip():
                response.failure("empty prediction")
            else:
                response.success()


@events.request.add_listener
def count_status_codes(response=None, exception=None, **_kwargs):
    if response is not None:
        STATUS_CODES[str(response.status_code)] += 1
    elif exception is not None:
        STATUS_CODES["exception"] += 1


@events.quitting.add_listener
def write_status_codes(**_kwargs):
    STATUS_OUTPUT.parent.mkdir(exist_ok=True)
    STATUS_OUTPUT.write_text(json.dumps(dict(STATUS_CODES), indent=2, sort_keys=True))
