import pika

# establishing connection with rabitmq server
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

def publish():
    print("publishing..")
    channel.basic_publish(exchange='',routing_key='admin',body='hello')

def send():
    print("sending..")
    channel.basic_publish(exchange='',routing_key='email',body='sended')

