FROM python:3.13-slim AS base

LABEL description="FastAPI Template"
LABEL version="0.1.0"

RUN apt-get update && apt-get install -y --no-install-recommends \
        libatomic1 wget make ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/env \
    PATH="/env/bin:${PATH}" \
    PYTHONPATH=/src

WORKDIR /src


FROM base AS app_builder
COPY pyproject.toml uv.lock /src/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-default-groups


FROM app_builder AS dev
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project


FROM base AS app
ARG VERSION
ENV VERSION=${VERSION:-0.1.0}
COPY --from=app_builder /env /env
COPY . /src
CMD ["uvicorn", "app.asgi:app", "--host", "0.0.0.0", "--proxy-headers", "--forwarded-allow-ips", "*"]
