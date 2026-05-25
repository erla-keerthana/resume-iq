FROM python:3.11-slim

# Install tesseract for OCR support
RUN apt-get update && \
    apt-get install -y --no-install-recommends tesseract-ocr && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create non-root user and set ownership of writable dirs
RUN useradd -r -s /bin/false appuser && \
    mkdir -p /app/uploads && \
    chown -R appuser:appuser /app

USER appuser

ENV PORT=8001
EXPOSE ${PORT}

CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}
