"""Call the deployed text recognizer /predict API with a support image."""
from pathlib import Path
import sys

import requests


DEFAULT_URL = "REPLACE_WITH_FUNCTION_URL"
IMAGE_PATH = Path("text_recognizer/tests/support/paragraphs/a01-077.png")


def main():
    base_url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    if base_url == DEFAULT_URL:
        raise SystemExit("Pass the Lambda Function URL as the first argument.")
    base_url = base_url.rstrip("/")

    with IMAGE_PATH.open("rb") as image_file:
        response = requests.post(
            f"{base_url}/predict",
            files={"image": (IMAGE_PATH.name, image_file, "image/png")},
            timeout=300,
        )

    print("Status:", response.status_code)
    print("Response:", response.json())


if __name__ == "__main__":
    main()
