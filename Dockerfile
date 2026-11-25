FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    FASTEMBED_CACHE_PATH=/app/.fastembed

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -c "from fastembed import TextEmbedding; TextEmbedding('sentence-transformers/all-MiniLM-L6-v2')"

COPY . .

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
