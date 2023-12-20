FROM python:3.10.12-slim-bookworm as builder

RUN python -m venv --copies /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY . .
RUN apt-get update && apt-get install -y git
RUN pip install -r requirements.txt .

FROM ghcr.io/equinor/isar:v1.16.10
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
