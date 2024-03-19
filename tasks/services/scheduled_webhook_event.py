import time

from utils.queue import send_queue
from utils.log import write_log
from utils.db import Database
import json


def update_task(data):
    Database().query("""
        UPDATE event 
        SET task_id = %(task_id)s, updated = %(updated)s
        WHERE id = %(event_id)s;
    """, data)


def scheduled_event_worker_handler(task_id, message):
    m = json.loads(message)
    event_id = m.get('event_id')
    update_task({
        "event_id": event_id,
        "task_id": str(task_id),
        "updated": time.time()
    })
    write_log(dict(
        event_id=event_id,
        status='CRE',
        payload=m,
        error=None
    ))
    send_queue(queue='delivery_queue', message=message)
