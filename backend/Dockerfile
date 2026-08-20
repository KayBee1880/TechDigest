# Debian-based, not Alpine: psycopg2-binary ships manylinux wheels built against
# glibc, not musl, so it silently fails to import on Alpine without extra work.
FROM python:3.13-slim

WORKDIR /app

RUN adduser --disabled-password --gecos "" appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER appuser

EXPOSE 5000

# docker-compose.yml overrides this per service (flask run for the API in dev,
# celery worker for the worker). This default is the prod-shaped command M7
# (deployment) will actually run.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
