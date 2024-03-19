import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_HOST = os.environ.get('DATABASE_HOST')
DATABASE_NAME = os.environ.get('DATABASE_NAME')
DATABASE_USERNAME = os.environ.get('DATABASE_USERNAME')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')

RABBITMQ_URL = os.environ.get('RABBITMQ_URL')

REDIS_URL = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0')

RETRY_THRESHOLD = int(os.environ.get('RETRY_THRESHOLD', '3'))

CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0')
CELERY_ENABLE_UTC = True
# CELERY_BEAT_SCHEDULE = {
#     "every-3-minutes": {
#         "task": "check_queue_size",
#         "schedule": 10,
#     },
# }

