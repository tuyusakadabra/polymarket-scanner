FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY src /app/src
COPY scripts /app/scripts
COPY configs /app/configs

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

CMD ["python", "-m", "polymarket_arb.cli", "scan"]
