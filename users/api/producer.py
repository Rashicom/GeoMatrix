import pika
import json

# establishing connection with rabitmq server
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# create a exchange
channel.exchange_declare(exchange='Normaluser_login_exchange', exchange_type='fanout')

# declare queue to bind exchange
channel.queue_declare(queue='normaluser_signup_cadastre')
channel.queue_declare(queue='normaluser_signup_blogs')

# bind queue to the exchange
channel.queue_bind(exchange='Normaluser_login_exchange',queue='normaluser_signup_cadastre')
channel.queue_bind(exchange='Normaluser_login_exchange',queue='normaluser_signup_blogs')




def signup_publish(data):
    """
    this fuction taking an argument data which consist nesessory details included for 
    updating user table 
    """

    for key in data:
        if data.get(key) == None:
            raise Exception("no enough data to perform signup publish.")
    
    print("publishing signup data..")
    channel.basic_publish(exchange='Normaluser_login_exchange',routing_key='',body=json.dumps(data))


def gov_user_signup_publish(data):
    """
    publishing gov uer signup details
    """

    print("publishing gov user signup")
    channel.basic_publish(exchange='',routing_key='gov_user_signup',body=json.dumps(data))




