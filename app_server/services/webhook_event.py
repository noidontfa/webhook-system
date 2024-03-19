import datetime
import time
import json
import uuid

import requests

from app_server.contrains.exception import InvalidAPIUsage
from app_server.repos.webhook_event import WebhookEventRepository
from utils.queue import send_queue
from utils.task import send_task
from utils.log import write_log
from utils import hmacsha1


class WebhookEventService:

    def __init__(self):
        self.repo = WebhookEventRepository()

    def subscribe(self, data):
        # Validate event type
        event_type_obj = self.repo.get_one_webhook_event(data.get('event_type'))
        if not event_type_obj:
            raise InvalidAPIUsage("event_type is not exited")

        # Check exist and save webhook event
        existed_we = self.repo.get_one_subscribed_webhook(event_type=data.get('event_type'),
                                                          user_id=data.get('user_id'))
        if existed_we:
            raise InvalidAPIUsage("event is subscribed already")
        res = self.repo.save_webhook(dict(
            url=data.get('url').strip(),
            event_type=data.get('event_type'),
            headers=data.get('headers'),
            secret_key=data.get('secret_key').strip(),
            user_id=data.get('user_id'),
            is_active=data.get('is_active', False),
            created=time.time(),
            updated=time.time()
        ))

        return {"webhook_id": res.id}

    def verify(self, data):
        # Validate webhook event
        webhook_id = data.get('webhook_id')
        if not webhook_id:
            raise InvalidAPIUsage("webhook_id is not existed")
        webhook = self.repo.get_one_webhook(webhook_id)
        if not webhook:
            raise InvalidAPIUsage("webhook not found")

        # Request webhook url
        url = str(webhook.url).strip()
        secret_key = webhook.secret_key
        token = str(uuid.uuid4())
        r = requests.post(url, json={"key": token})
        if r.status_code != 200:
            raise InvalidAPIUsage("Verification failed")

        # Verify signature
        hmac = r.json().get('hmac')
        if not hmacsha1.verify(secret_key, token, hmac):
            raise InvalidAPIUsage("Invalid Signature")
        self.repo.active_webhook(dict(webhook_id=webhook_id, updated=time.time()))

    def trigger(self, data):
        # Validate trigger event type
        trigger_type = data.get('trigger_type')
        execution_date = data.get('execution_date')
        now = time.time()
        if trigger_type == 'SCHEDULED':
            if not execution_date:
                raise InvalidAPIUsage("Missing execution date")
            if now > execution_date:
                raise InvalidAPIUsage("Only schedule the future event")

        # Validate webhook event
        event_type = data.get('event_type')
        user_id = data.get('user_id')
        webhook = self.repo.get_one_subscribed_webhook(event_type, user_id)
        if not webhook:
            raise InvalidAPIUsage("webhook not found")

        # Save and delivery webhook event
        p = dict(
            webhook_id=webhook.id,
            event_type=event_type,
            user_id=user_id,
            execution_date=execution_date if trigger_type == 'SCHEDULED' else time.time(),
            metadata={
                "url": webhook.url,
                "headers": webhook.headers,
                "payload": data.get('payload'),
                "hmac": hmacsha1.generate(webhook.secret_key, f"{event_type}")  # For simplify
            },
            status="CRE",
            created=time.time(),
            updated=time.time()
        )
        res = self.repo.save_event(p)
        p['event_id'] = res.id
        if trigger_type == 'NOW':
            write_log(dict(
                event_id=p['event_id'],
                status='CRE',
                payload=p,
                error=None
            ))
            send_queue(queue='delivery_queue', message=p)
        if trigger_type == 'SCHEDULED':
            eta = datetime.datetime.utcnow() + datetime.timedelta(seconds=execution_date - now)
            print("eta: ", eta)
            send_task(
                name='scheduled_event_worker',
                eta=eta,
                args=[json.dumps(p)]
            )

        return p
