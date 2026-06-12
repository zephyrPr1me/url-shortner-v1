FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app


COPY pyproject.toml uv.lock ./


RUN uv sync --frozen --no-install-project

COPY . .


RUN uv sync --frozen


FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app


COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH"


CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
