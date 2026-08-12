FROM python:3.12-slim-bookworm AS base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY pyproject.toml uv.lock README.md ./
COPY src ./src

FROM base AS runtime
RUN uv sync --frozen --no-dev
ENTRYPOINT ["uv", "run", "homelab-hdmi-switch"]

FROM runtime AS test
RUN uv sync --frozen
COPY tests ./tests
ENTRYPOINT ["uv", "run", "pytest"]

FROM test AS ruff
ENTRYPOINT ["uv", "run", "ruff"]

FROM test AS ty
ENTRYPOINT ["uv", "run", "ty"]
