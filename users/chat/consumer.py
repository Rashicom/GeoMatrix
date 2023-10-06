from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from api.models import Messages, Conversation
from .serializers import ChatMessageSerializer
from django.db.models import Q
import json


class ChatConsumer(WebsocketConsumer):

    def connect(self):
        """
        this method establishing long lived connection with the user
        accept : room_name (format:UUID)
                 tocken (in params named as tocken, jwt)
        
        WARNING: this method is called only if the tocken is validated, routing is wraped by jwt authentication class in the asgi config

        """

        print("connecting ....")

        # fetchind authenticated user instance and room_name
        user = self.scope["user"]
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]

        # create root_group_name string starts with chat_
        self.room_group_name = f"chat_{self.room_name}"
        
        """
        By default the send(), group_send(), group_add() and other functions are async functions, 
        meaning you have to await them. If you need to call them from synchronous code, 
        you'll need to use the handy asgiref.sync.async_to_sync wrapper:
        """

        # join room group
        # here async_to_sync(self.channel_layer.group_add) returning another function
        # converting group_add async function to sync function
        sync_group_add = async_to_sync(self.channel_layer.group_add)
        
        # channel_name is defined by django when a websocket connection created
        # every socket connection have a unique channel_name it represent wich user is conneted from a instace
        # now we are including this websicket connection to send/recive message from room_group_name
        sync_group_add(self.room_group_name,self.channel_name)
        
        # before proceding to connect we have to assert the user is in either a initiator or a reciever in the room
        conversation_filter = Q(room = self.room_name) & (Q(initiator=user) | Q(reciever=user))
        
        # if user not a part of room we reject
        if not Conversation.objects.filter(conversation_filter).exists():
            """
            if the user is not a part of provided room close the connection 
            """
            print("rejecting..")
            self.close()

        # else we procede to connect
        else:    
            print("CONNECTED TO", self.room_group_name)
            self.accept()
        

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )
    

    # Receive message from WebSocket
    def receive(self, text_data):

        # parse the json data into dictionary object
        text_data_json = json.loads(text_data)
        
        # send the message to the group which socket connected to
        # a function named as chat_message must be defined to handle / recieve message
        # type is usefull to call defferent fuction based on the recieve state like typing.., chat_message
        chat_type = {"type": "chat_message"}
        return_dict = {**chat_type, **text_data_json}

        # get a sync function for sending message
        sync_send = async_to_sync(self.channel_layer.group_send)
        
        # update to database
        sender = self.scope["user"]
        message_text = text_data_json["message"]
        room = self.room_name
        conversaton_instance = Conversation.objects.get(room=room)
        

        serializer = ChatMessageSerializer(data={"room": conversaton_instance.id, "sender": sender.id, "text": message_text})
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except Exception as e:
            print(e)
            

        # send message to the room which we connected to
        sync_send(self.room_group_name, return_dict)


    # Receive message from room group
    def chat_message(self, event):
        """
        this fuction is called if the chat_type is chat_message
        means message is sended
        """

        # copy the event, becouse this is a async and longlived connection 
        # another user and functin may use the same data, so we have to proserve
        # by coping we assert that original message wont interepted
        text_data_json = event.copy()
        text_data_json.pop("type")
        
        # getting message and attachments. attachments is may or may not be present in the data. thats why we use .get()
        message, attachments = (text_data_json["message"], text_data_json.get("attachments"))

        # then send to message to the websocket target user can see the message
        self.send(text_data=json.dumps(text_data_json))