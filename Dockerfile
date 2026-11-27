# arm64 digests — this image is deployed to pi5-8 (a Raspberry Pi) for
# physical serial access to the switch, not a generic/amd64 target.
#
# release and test each have their own external FROM instead of extending
# a shared base stage: kaniko pushes a Docker-v2-schema manifest (which
# zot rejects with 415/MANIFEST_INVALID) when a pushed --target stage's
# own FROM references another Dockerfile stage rather than an external
# image. common below is never pushed itself, so COPY --from=common
# doesn't trigger this.

FROM python:3.12-slim-bookworm@sha256:fa161ca9d626b475d504c439b943e295fbca9e2560b1be14654ade60e7d8d45a AS common
COPY --from=ghcr.io/astral-sh/uv:latest@sha256:8ba8ac26ed7be9ce3f0fbd510f8d26a3fb9b19056efe6c08433baf9762129edd /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
RUN uv sync --frozen --no-dev

FROM python:3.12-slim-bookworm@sha256:fa161ca9d626b475d504c439b943e295fbca9e2560b1be14654ade60e7d8d45a AS release
COPY --from=common /bin/uv /bin/uvx /bin/
WORKDIR /app
COPY --from=common /app ./
ARG COMMIT_SHA
ENV COMMIT_SHA=$COMMIT_SHA
EXPOSE 8000
ENTRYPOINT ["uv", "run", "gunicorn", "homelab_hdmi_switch.wsgi:app", "--bind", "0.0.0.0:8000"]

FROM python:3.12-slim-bookworm@sha256:fa161ca9d626b475d504c439b943e295fbca9e2560b1be14654ade60e7d8d45a AS test
COPY --from=common /bin/uv /bin/uvx /bin/
WORKDIR /app
COPY --from=common /app ./
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
RUN uv sync --frozen
COPY tests ./tests
ENTRYPOINT ["uv", "run"]
