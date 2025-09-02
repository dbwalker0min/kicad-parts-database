FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
 && curl -LsSf https://astral.sh/uv/install.sh | sh \
 && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:${PATH}"
ENV UV_PROJECT_ENVIRONMENT=/app/.venv
ENV UV_PYTHON=3.12
ENV PYTHONPATH=/app:/app/src

COPY pyproject.toml ./
RUN uv sync --no-dev

COPY src ./src
COPY test ./test

CMD ["uv", "run", "test/bootstrap_db.py"]
