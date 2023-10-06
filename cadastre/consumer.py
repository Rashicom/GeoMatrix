import pika
import json
import django
from sys import path
from os import environ

path.append('/home/rashi/Microservice projects/GeoMatrix/cadastre/config/settings.py')
environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings') 
django.setup()
from api.serializers import NormalUserSerializer, GovbodyUserSerializer, GovbodyUserAddressSerializer
from django.contrib.auth.hashers import make_password

'-------------------- CALL BACK FUNCTIONS ---------------'
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
    if serializer.is_valid():

        # hashing password
        hashed_password = make_password(serializer.validated_data.get("password"))

        try:
            serializer.save(password=hashed_password)
            
            # acknowledge that messate process success and dequeue messag fromt the queue
            # else message remains in the queue until a acknoledge came
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print("cant update normal user")


        print("normal user created")
    else:
        print("cant update table for login")
    


# gov body signup
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

    # hashing password
    hashed_password = make_password(serializer.validated_data.get("password"))
    
    try:

        gov_user_instance = serializer.save(password=hashed_password,is_active=True)
        address_serializer.save(gov_body=gov_user_instance)

        # acknowledge that messate process success and dequeue messag fromt the queue
        # else message remains in the queue until a acknoledge came
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    except Exception as e:
        print("cant update gov gov user")







'---------------- CHANNEL AND QUEUE CONFIGUE ----------'
# establishing connection with rabitmq server
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()




'--------------------- QUEUE DECLARE ----------------------'
# queue
channel.queue_declare(queue='normaluser_signup_cadastre')
channel.queue_declare(queue='govuser_signup_cadastre')



'------------------ CONSUMING FROM QUEUE -----------------'
# consuming from queue
channel.basic_consume(queue='normaluser_signup_cadastre', on_message_callback=normal_user_signup_consume)
channel.basic_consume(queue='govuser_signup_cadastre', on_message_callback=gov_user_signup_consume)





print("started consuming..")
channel.start_consuming()
channel.close()
