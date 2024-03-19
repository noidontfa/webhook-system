import json
import time

import requests
import datetime

import config
from utils.execution_calculator import RepeatEveryNMinutes
from utils.log import write_log
from utils.task import send_task


class WebhookEventHandler:

    def __init__(self):
        self.error_handler = RepeatEveryNMinutes()

    def delivery(self, message):
        data = json.loads(message)
        url = data.get('metadata', {}).get('url')
        headers = data.get('metadata', {}).get('headers')
        payload = data.get('metadata', {}).get('payload')
        hmac = data.get('metadata', {}).get('hmac')
        headers['HMAC'] = hmac
        event_id = data.get('event_id')
        execution_date = data.get('execution_date')
        user_id = data.get('user_id')
        event_type = data.get('event_type')
        write_log(dict(
            event_id=data.get('event_id'),
            status='HAN',
            payload=payload,
            error=None
        ))
        try:
            # Delivery data
            r = requests.post(url, json=dict(
                event_type=event_type,
                user_id=user_id,
                payload=payload,
                execution_date=execution_date
            ), headers=headers)
            r.raise_for_status()
            payload = r.json()
            write_log(dict(
                event_id=event_id,
                status='SUC',
                payload=payload,
                error=None
            ))
        except requests.exceptions.HTTPError as err:
            # Calculate retry times and check with the threshold
            retry = data.get('metadata', {}).get('retry', 0) + 1
            if retry > config.RETRY_THRESHOLD:
                write_log(dict(
                    event_id=event_id,
                    status='ERR',
                    payload=None,
                    error={
                        "error": str(err),
                        "message": "Retry Stopped"
                    }
                ))
                return

            # Calculate the execution date and register with celery
            print("retry times: ", retry)
            new_execution_date = self.error_handler.calculate_date(execution_date)
            eta = datetime.datetime.utcnow() + datetime.timedelta(seconds=new_execution_date - time.time())
            data['execution_date'] = new_execution_date
            data['metadata']['eta'] = str(eta)
            data['metadata']['retry'] = retry
            send_task(name='scheduled_event_worker', args=[json.dumps(data)], eta=eta)
            write_log(dict(
                event_id=event_id,
                status='ERR',
                payload=None,
                error={
                    "error": str(err)
                }
            ))
        except Exception as err:
            write_log(dict(
                event_id=event_id,
                status='ERR',
                payload=None,
                error={
                    "error": str(err)
                }
            ))
