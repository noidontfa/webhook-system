from celery import Celery


def create_celery():
    c = Celery(__name__)
    c.config_from_object('config', namespace='CELERY')
    return c


def send_task(name, args, **kwargs):
    return create_celery().send_task(name, args=args, **kwargs)