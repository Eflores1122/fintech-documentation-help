FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-spa fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY rules ./rules
RUN pip install --no-cache-dir .

EXPOSE 8000
CMD ["fdh", "serve", "--host", "0.0.0.0", "--port", "8000"]
