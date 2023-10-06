import pika
import json
import django
from sys import path
from os import environ
import time

path.append('/home/rashi/Microservice projects/GeoMatrix/blog/config/settings.py')
environ.setdefault('DJANGO_SETTINGS_MODULE', 'confiq.settings')
django.setup()



"--------------------- CALL BACK FUNCTIONS --------------------------"

from api.serializers import NormalUserSignupSerializer, GovBodyAddressSerializer,GovSignupSeriaizers
from django.contrib.auth.hashers import make_password


# normal user signup consumer
def normal_user_signup_consume(ch,method,properties, body):
    """
    this fuction is calling when a request is came to the signup que which is
    indicating that a new user is created in the users service.
    body is contains enough information to save the user info here too.
    """
    print("data from signup que...")
    
    # get data and serializing
    user_data = json.loads(body)
    serializer = NormalUserSignupSerializer(data=user_data)

    # validating data and update the table
    if serializer.is_valid():

        # hashing password and save
        hashed_password = make_password(serializer.validated_data.get("password"))
        serializer.save(password=hashed_password)
        print("normal user created")

        # acknowledge that messate process success and dequeue messag fromt the queue
        # else message remains in the queue until a acknoledge came
        ch.basic_ack(delivery_tag=method.delivery_tag)
    else:
        print("cant update table for login")



# gov body signup consumer
def gov_user_signup_consume(ch,method,properties,body):
    """
    creating gov user
    """
    print("data from signup que...")
    # get data and serializing
    user_data = json.loads(body)
    serializer = GovSignupSeriaizers(data=user_data.get("user"))
    address_serializer = GovBodyAddressSerializer(data=user_data.get("address"))
    

    if serializer.is_valid() and address_serializer.is_valid():
        try:
            # hashing password
            hashed_password = make_password(serializer.validated_data.get("password"))
            gov_user_instance = serializer.save(password=hashed_password,is_active=True)
            address_serializer.save(gov_body=gov_user_instance)

            # acknowledge that messate process success and dequeue messag fromt he queue
            # else message remains in the queue until a acknoledge came
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print("cant update gov gov user")
    
    else:
        print("invalied fields")

    


"-------------------- CHANNEL AND QUEUE CONFIG --------------------"
# establishing connection with rabbitMQ server
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()




'------------------------ QUEUE DECLARE ---------------------------'
# queue
channel.queue_declare(queue='normaluser_signup_blogs')
channel.queue_declare(queue='govuser_signup_blogs')




'-------------------- CONSUMING FROM QUEUE ------------------------'
# consuming from queue
channel.basic_consume(queue='normaluser_signup_blogs',on_message_callback=normal_user_signup_consume)
channel.basic_consume(queue='govuser_signup_blogs',on_message_callback=gov_user_signup_consume)



print("started consuming..")
channel.start_consuming()
channel.close()
