FROM python:3.10-slim as builder

RUN python -m venv --copies /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY . .
RUN pip install .

FROM ghcr.io/equinor/isar:v1.13.2
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
