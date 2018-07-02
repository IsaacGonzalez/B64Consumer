#!/usr/bin/env python
import pika
import sys
import base64
import json
import time

def main():

    connection = pika.BlockingConnection(
        pika.ConnectionParameters
        (host='192.168.1.133', 
        credentials=pika.PlainCredentials('biometrico', 'biom3tric0')))
    channel = connection.channel()

    channel.exchange_declare(exchange='f_compara',
                             exchange_type='fanout')

    result = channel.queue_declare(exclusive=True)
    queue_name = result.method.queue

    severities = sys.argv[1:]
    if not severities:
        sys.stderr.write("Usage: %s [info] [warning] [error]\n" % sys.argv[0])
        sys.exit(1)

    for severity in severities:
        channel.queue_bind(exchange='f_compara',
                           queue=queue_name,
                           routing_key='')

    print(' [*] Waiting for logs. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        print(" [x] %r:%r" % (method.routing_key, body[0:100]))

        json_body = json.loads(body)

        print(json_body['b64'])
        with open('{}.jpg'.format(time.time()), "wb") as fh:
            fh.write( base64.b64decode(json_body['b64']))


    channel.basic_consume(callback,
                          queue=queue_name,
                          no_ack=True)

    channel.start_consuming()

if __name__ == "__main__":
    main()