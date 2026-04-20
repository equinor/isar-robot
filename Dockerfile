# Based on recommendations from
# https://snyk.io/blog/best-practices-containerizing-python-docker/
FROM python:3.14-slim AS build

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends git build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .
RUN --mount=source=.git,target=.git,type=bind uv sync --frozen --no-editable --no-dev

FROM python:3.14-slim
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
