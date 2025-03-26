# Based on recommendations from
# https://snyk.io/blog/best-practices-containerizing-python-docker/
FROM python:3.13-slim as build

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

FROM python:3.13-slim
WORKDIR /app
COPY --from=build /app/venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

EXPOSE 3000

# Env variable for ISAR to know it is running in docker
ENV IS_DOCKER=true

# Add non-root user
RUN useradd --create-home --shell /bin/bash 1000
RUN chown -R 1000 /app
RUN chmod 755 /app
USER 1000

CMD ["isar-start"]
