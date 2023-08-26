import pika

# establishing connection with rabitmq server
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()


channel.queue_declare(queue='signup')


def callback(ch,method,properties, body):
    print("reponse done")
    print(body)


channel.basic_consume(queue='signup', on_message_callback=callback)


print("started consuming..")

channel.start_consuming()
channel.close()