# Based on recommendations from
# https://snyk.io/blog/best-practices-containerizing-python-docker/
FROM ghcr.io/astral-sh/uv:0.13.1@sha256:4a1f3666816dafadd20ceb71eac9a7d56d7ef30279f7d64048519ab901ada336 AS uv
FROM python:3.14-slim@sha256:a2b82f3c48559aa0a8446d9af49826b6e2b2016f4cd2afabfe6013ec53729170 AS build

COPY --from=uv /uv /uvx /bin/

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends git build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .
RUN --mount=source=.git,target=.git,type=bind uv sync --frozen --no-editable --no-dev

FROM python:3.14-slim@sha256:a2b82f3c48559aa0a8446d9af49826b6e2b2016f4cd2afabfe6013ec53729170
WORKDIR /app
COPY --from=build /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 3000

# Env variable for ISAR to know it is running in docker
ENV IS_DOCKER=true

# Add non-root user
RUN useradd --create-home --uid 1000 --shell /bin/bash app
RUN chown -R 1000 /app
RUN chmod 755 /app
USER 1000

CMD ["isar-start"]
