import pika
import json

# establishing connection with rabitmq server
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

def signup_publish(data):
    """
    this fuction taking an argument data which consist nesessory details included for 
    updating user table 
    """

    for key in data:
        if data.get(key) == None:
            raise Exception("no enough data to perform signup publish.")
    
    print("publishing signup data..")
    channel.basic_publish(exchange='',routing_key='signup',body=json.dumps(data))

