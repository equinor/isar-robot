# Based on recommendations from
# https://snyk.io/blog/best-practices-containerizing-python-docker/
FROM ghcr.io/astral-sh/uv:0.12.9@sha256:8b940d3a9d65bed080436972241af2e21c84b5e8c9193f7014ed71479ee795ff AS uv
FROM python:3.14-slim@sha256:ce40764625a4ff50df3548277632e7f96c4e77fe75fa848aae9885476e7df5a4 AS build

COPY --from=uv /uv /uvx /bin/

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends git build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .
RUN --mount=source=.git,target=.git,type=bind uv sync --frozen --no-editable --no-dev

FROM python:3.14-slim@sha256:ce40764625a4ff50df3548277632e7f96c4e77fe75fa848aae9885476e7df5a4
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
