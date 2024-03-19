import utils.queue as queue
from message_queue.services.webhook_handler import WebhookEventHandler


def callback(ch, method, properties, body):
    print(f" [x] Received {body.decode()}")
    WebhookEventHandler().delivery(body.decode())
    print(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)


queue.create_consumer(queue='delivery_queue', callback=callback)
