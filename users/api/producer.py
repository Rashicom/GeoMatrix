import pika

# establishing connection with rabitmq server
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

def signup_publish():
    print("publishing..")
    channel.basic_publish(exchange='',routing_key='signup',body="hello there")
