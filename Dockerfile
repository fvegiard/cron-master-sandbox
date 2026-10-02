FROM python:3.14-slim@sha256:0741d101873c12ab927e6f8653feb8862b9bd58771177acb1b885b95141f91b4
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HOME=/tmp REPORT_DIR=/tmp/reports
WORKDIR /app
COPY requirements-test.lock .
RUN python -m pip install --no-cache-dir --disable-pip-version-check --require-hashes --only-binary=:all: -r requirements-test.lock
COPY . .
USER 10001:10001
CMD ["python", "scripts/sandbox_probe.py"]
