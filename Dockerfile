FROM python:3.14-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HOME=/tmp
WORKDIR /app
COPY requirements-test.txt .
RUN python -m pip install --no-cache-dir --disable-pip-version-check -r requirements-test.txt
COPY . .
USER 10001:10001
CMD ["python", "-m", "unittest", "discover", "-s", "tests", "-v"]
