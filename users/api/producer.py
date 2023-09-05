import pika
import json

# establishing connection with rabitmq server
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()



'--------------------- EXCHANGE DECLARE --------------------'
# create a exchange
# exchange for normal user signup
channel.exchange_declare(exchange='Normaluser_login_exchange', exchange_type='fanout')

# exchange for gov user signup
channel.exchange_declare(exchange='Govuser_login_exchange', exchange_type='fanout')




'---------------------- QUEUE DECLARE -------------------------'
# Normal user queues
channel.queue_declare(queue='normaluser_signup_cadastre')
channel.queue_declare(queue='normaluser_signup_blogs')

# gov user queues
channel.queue_declare(queue='govuser_signup_cadastre')
channel.queue_declare(queue='govuser_signup_blogs')




'------------------ BIND QUEUE WITH EXCHANGE --------------------'
# bind normal user login que with exchange: Normaluser_login_exchange
channel.queue_bind(exchange='Normaluser_login_exchange',queue='normaluser_signup_cadastre')
channel.queue_bind(exchange='Normaluser_login_exchange',queue='normaluser_signup_blogs')

# bind normal user login que with exchange: Govuser_login_exchange
channel.queue_bind(exchange='Govuser_login_exchange', queue='govuser_signup_cadastre')
channel.queue_bind(exchange='Govuser_login_exchange', queue='govuser_signup_blogs')





'------------------- PUBLISHIGN METHODS -----------------------'

# publish normal user signup
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



# publish gov user signup
def gov_user_signup_publish(data):
    """
    publishing gov uer signup details
    """

    print("publishing gov user signup")
    channel.basic_publish(exchange='Govuser_login_exchange',routing_key='',body=json.dumps(data))




