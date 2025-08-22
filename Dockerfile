FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y gcc libpq-dev python3-dev build-essential curl && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app/
COPY uv.lock* uv.toml* /app/

RUN pip install --upgrade pip uv && \
    uv pip install --system -e .

COPY . /app

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

CMD ["sh", "/app/entrypoint.sh"]