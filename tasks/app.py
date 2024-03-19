from tasks.services.scheduled_webhook_event import scheduled_event_worker_handler
from utils.task import create_celery
from celery.utils.log import get_task_logger

C = create_celery()

logger = get_task_logger(__name__)


@C.task(name='scheduled_event_worker', bind=True)
def scheduled_event_worker(self, message):
    logger.info(message)
    logger.info(self.request.id)
    scheduled_event_worker_handler(task_id=self.request.id, message=message)


@C.task(name='check_queue_size')
def check_queue_size():
    print("me tick")
    logger.info('check_queue_size tick')
