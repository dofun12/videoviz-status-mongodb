import json

import pika
from pika.adapters.blocking_connection import BlockingChannel

from database.db_manager import DBManager

EXCHANGE_STATUS = 'status_publisher'
QUEUE_STATUS = 'store_queue'


class Callbacker:
    def __init__(self):
        self.db = DBManager()

    def callback(self, ch: BlockingChannel, method, properties, body: bytes):
        encoding = 'utf-8'
        text = body.decode(encoding)
        try:
            self.db.insert(db_name='videoviz', collection='status', data=json.loads(body))
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(e)

        print(" [x] Received " + text)


class Listener:

    def declare(self, channel: BlockingChannel):
        channel.queue_declare(queue=QUEUE_STATUS, durable=True)
        channel.exchange_declare(exchange=EXCHANGE_STATUS, exchange_type='fanout', durable=True)
        channel.queue_bind(queue=QUEUE_STATUS, exchange=EXCHANGE_STATUS)

    def __init__(self):
        self.credentials = pika.PlainCredentials('guest', 'guest')
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='192.168.15.101', credentials=self.credentials))

    def publish(self, message):
        channel = self.connection.channel()
        self.declare(channel)
        channel.queue_declare(queue='hello')
        channel.basic_publish(exchange='',
                              routing_key='hello',
                              body=message)
        print(" [x] Sent 'Hello World!'")

    def listen(self):
        channel = self.connection.channel()
        self.declare(channel)
        callbacker = Callbacker()
        channel.basic_consume(queue=QUEUE_STATUS,
                              auto_ack=False,
                              on_message_callback=callbacker.callback)

        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()
