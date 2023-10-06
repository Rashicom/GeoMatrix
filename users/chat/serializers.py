from rest_framework import serializers
from api.models import CustomUser,Messages,Conversation


"""----------------------CHAT SERIALIZERS---------------"""     


# custom user serilaizer
class UserSerilaizer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email','contact_number','profile_photo']



# chating serializer
class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = '__all__'


# conversation serializer
class ConversationSerializer(serializers.ModelSerializer):
    initiator = UserSerilaizer()
    reciever = UserSerilaizer()
    class Meta:
        model = Conversation
        fields = ['room','initiator','reciever','start_time']