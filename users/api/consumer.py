import pika

# establishing connection with rabitmq server
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='admin')
channel.queue_declare(queue='email')


def callback(ch,method,properties, body):
    print("reponse done")

def email_callback(ch,method,properties, body):
    print("email requests came")

channel.basic_consume(queue='admin', on_message_callback=callback, auto_ack=True)
channel.basic_consume(queue='email', on_message_callback=email_callback)


print("started consuming..")

channel.start_consuming()
channel.close()
