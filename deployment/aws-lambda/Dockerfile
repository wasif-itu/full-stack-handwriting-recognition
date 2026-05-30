FROM public.ecr.aws/lambda/python:3.10

ENV PYTHONUNBUFFERED=1 \
    TORCH_NUM_THREADS=2

COPY requirements.txt .
RUN pip install --upgrade pip==23.1.2 && pip install --no-cache-dir -r requirements.txt

COPY text_recognizer/ ./text_recognizer
COPY api.py ./api.py

CMD ["api.handler"]
