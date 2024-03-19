import pika
import config
import json


def send_queue(queue, message):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=config.RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)

    msg = message if isinstance(message, str) else json.dumps(message)
    channel.basic_publish(
        exchange='',
        routing_key=queue,
        body=msg,
        properties=pika.BasicProperties(
            delivery_mode=pika.DeliveryMode.Persistent
        ))
    print(f" [x] Sent {message}")
    connection.close()


def create_consumer(queue, callback):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=config.RABBITMQ_URL)
    )
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=callback)
    channel.start_consuming()
