FROM python:3.11-slim-buster


WORKDIR /opt/ws

RUN mkdir -p /opt/ws/beat # celery beat folder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV DATABASE_NAME=webhook_system_prod
ENV DATABASE_HOST=127.0.0.1
ENV DATABASE_USERNAME=admin
ENV DATABASE_PASSWORD=admin
ENV REDIS_URL=redis://127.0.0.1:6379/0
ENV RABBITMQ_URL=127.0.0.1
ENV RETRY_THRESHOLD=3

COPY . .

RUN pip install -r requirements.txt

CMD ["gunicorn", "-w", "4", "app_server.controllers.api:app"]