FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    N3_PERSIST_ROOT=/app/data

WORKDIR /app

RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir namel3ss

COPY . /app

RUN mkdir -p /app/data

EXPOSE 7340

CMD ["sh", "-c", "n3 studio app.ai --port ${PORT:-7340}"]
