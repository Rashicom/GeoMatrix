import pika
import json
import django
from sys import path
from os import environ

path.append('/home/rashi/Microservice projects/GeoMatrix/cadastre/config/settings.py')
environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings') 
django.setup()
from api.serializers import NormalUserSerializer, GovbodyUserSerializer, GovbodyUserAddressSerializer



# signup consumer
def normal_user_signup_consume(ch,method,properties, body):
    """
    this fuction is calling when a request is came to the signup que which is
    indicating that a new user is created in the users service.
    body is contains enough information to save the user info here too.
    """
    print("data from signup que...")
    
    # get data and serializing
    user_data = json.loads(body)
    serializer = NormalUserSerializer(data=user_data)

    # validating data and update the table
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        print("normal user created")
    else:
        print("cant update table for login")
    


def gov_user_signup_consume(ch,method,properties,body):
    """
    creating gov user
    """
    print("data from signup que...")
    # get data and serializing
    user_data = json.loads(body)
    serializer = GovbodyUserSerializer(data=user_data.get("user"))
    address_serializer = GovbodyUserAddressSerializer(data=user_data.get("address"))
    serializer.is_valid()
    address_serializer.is_valid()
    
    try:
        gon_user_instance = serializer.save()
        address_serializer.save(gov_body=gon_user_instance)
    except Exception as e:
        print("cant update gov gov user")

def test_consume(ch,method,properties,body):
    print(body)


# establishing connection with rabitmq server
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()





# queue
channel.queue_declare(queue='normaluser_signup_cadastre')
channel.queue_declare(queue='gov_user_signup')
channel.queue_declare(queue='test2')


# consuming from queue
channel.basic_consume(queue='normaluser_signup_cadastre', on_message_callback=normal_user_signup_consume, auto_ack=True)
channel.basic_consume(queue='gov_user_signup', on_message_callback=gov_user_signup_consume, auto_ack=True)
channel.basic_consume(queue='test2',on_message_callback=test_consume, auto_ack=True)





print("started consuming..")
channel.start_consuming()
channel.close()
