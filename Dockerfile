FROM python:3.12-slim-bookworm@sha256:fa161ca9d626b475d504c439b943e295fbca9e2560b1be14654ade60e7d8d45a AS base
# arm64 digests — this image is deployed to pi5-8 (a Raspberry Pi) for
# physical serial access to the switch, not a generic/amd64 target.
COPY --from=ghcr.io/astral-sh/uv:latest@sha256:8ba8ac26ed7be9ce3f0fbd510f8d26a3fb9b19056efe6c08433baf9762129edd /uv /uvx /bin/
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY pyproject.toml uv.lock README.md ./
COPY src ./src

FROM base AS release
ARG COMMIT_SHA
ENV COMMIT_SHA=$COMMIT_SHA
RUN uv sync --frozen --no-dev
EXPOSE 8000
ENTRYPOINT ["uv", "run", "gunicorn", "homelab_hdmi_switch.wsgi:app", "--bind", "0.0.0.0:8000"]

FROM release AS test
RUN uv sync --frozen
COPY tests ./tests
ENTRYPOINT ["uv", "run"]

