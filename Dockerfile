# Hugging Face Docker Space entrypoint
# Keep identical to server/Dockerfile so HF builds from repo root.

ARG BASE_IMAGE=ghcr.io/meta-pytorch/openenv-base:latest
FROM ${BASE_IMAGE} AS python_builder

WORKDIR /app/env
COPY . /app/env

RUN if ! command -v uv >/dev/null 2>&1; then \
        curl -LsSf https://astral.sh/uv/install.sh | sh && \
        mv /root/.local/bin/uv /usr/local/bin/uv && \
        mv /root/.local/bin/uvx /usr/local/bin/uvx; \
    fi

RUN --mount=type=cache,target=/root/.cache/uv \
    if [ -f uv.lock ]; then uv sync --frozen --no-editable; else uv sync --no-editable; fi

# Build the Phaser UI (Vite) in a dedicated node stage and copy dist into the image.
FROM node:22-bookworm-slim AS web_builder
WORKDIR /web
COPY web/package.json web/package-lock.json /web/
RUN npm ci
COPY web/ /web/
RUN npm run build

FROM ${BASE_IMAGE}
WORKDIR /app/env
COPY --from=python_builder /app/env/.venv /app/.venv
COPY --from=python_builder /app/env /app/env
COPY --from=web_builder /web/dist /app/env/web/dist

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/env:$PYTHONPATH"
# CPU Spaces: cap oracle LLM load+infer so /demo/step returns (baseline fallback) instead of hanging the tab.
ENV DEMO_ORACLE_INFERENCE_TIMEOUT_SEC="120"

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["sh", "-c", "cd /app/env && uvicorn server.app:app --host 0.0.0.0 --port 8000"]

