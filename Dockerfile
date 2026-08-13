FROM python:3.12-slim-bookworm@sha256:4766d8b510c428e595d74b9cc5bbb2fae8e26316fffb4adc89908d79aacd58a2 AS base
COPY --from=ghcr.io/astral-sh/uv:latest@sha256:2d890623d310b57771ce840f0da5eed5fc6d657da05ffaa45d82797b53fa3abc /uv /uvx /bin/
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY pyproject.toml uv.lock README.md ./
COPY src ./src

FROM base AS release
RUN uv sync --frozen --no-dev
EXPOSE 8000
ENTRYPOINT ["uv", "run", "gunicorn", "homelab_hdmi_switch.wsgi:app", "--bind", "0.0.0.0:8000"]

FROM release AS test
RUN uv sync --frozen
COPY tests ./tests
ENTRYPOINT ["uv", "run"]

