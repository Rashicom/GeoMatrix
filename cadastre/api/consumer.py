import pika
import json

# establishing connection with rabitmq server
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()


channel.queue_declare(queue='signup')

# signup consumer
def signup_consume(ch,method,properties, body):
    """
    this fuction is calling when a request is came to the signup que which is
    indicating that a new user is created in the users service.
    body is contains enough information to save the user info here too.
    """

    try:
        print("reponse done")
        x = json.loads(body)
        print(x)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print("exception found")
        


channel.basic_consume(queue='signup', on_message_callback=signup_consume)




print("started consuming..")

channel.start_consuming()
channel.close()