# Based on recommendations from
# https://snyk.io/blog/best-practices-containerizing-python-docker/
FROM python:3.10-slim as build

WORKDIR /app

RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

RUN apt-get update && apt-get install -y git
RUN apt-get install -y --no-install-recommends build-essential gcc

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN --mount=source=.git,target=.git,type=bind
RUN pip install .

FROM ghcr.io/equinor/isar:v1.16.14
WORKDIR /app
COPY --from=build /app/venv /app/venv
ENV PATH="/app/venv/bin:$PATH"
