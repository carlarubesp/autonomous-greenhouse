# Build context: repository root (see docker-compose.yml).
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.13.9 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

# Dependencies first, so this layer is cached until the lockfile changes.
WORKDIR /src
COPY pyproject.toml uv.lock ./
COPY monitor/pyproject.toml monitor/
RUN uv sync --frozen --no-dev --package greenhouse-monitor

WORKDIR /app
COPY monitor/ .

CMD ["python", "monitor.py"]
