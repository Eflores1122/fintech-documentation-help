FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY rules ./rules
RUN pip install --no-cache-dir .

EXPOSE 8000
CMD ["fdh", "serve", "--host", "0.0.0.0", "--port", "8000"]
