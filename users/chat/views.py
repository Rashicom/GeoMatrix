from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import ConversationSerializer
from api.models import CustomUser, Conversation, Messages
from django.db.models import Q

# Create your views here.

class StartConversation(APIView):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ConversationSerializer

    def post(self, request, format=None):
        """
        accept: reciever (to which user we start communication)
        
        this method is start a conversation by start with a lookup in database
        
        collecting all conversations where the the request.user and reciever are participated(only one exist if there is any previous chat)
        if conversation exist collect chat history and return
        if conversation does not exist start a new conversation
        """

        # fetching the reciever
        reciever = request.data.get('reciever')

        # fetching reciever instance for database if exist, else return does not exist message
        try:
            participant = CustomUser.objects.get(email=reciever)
            
        except CustomUser.DoesNotExist:
            return Response({"details":"reciever does not exist"})
        
        # collecting conversation if any
        q_fiter = Q(initiator=request.user.id, reciever=participant.id) | Q(initiator=participant.id, reciever=request.user.id)
        conversation = Conversation.objects.filter(q_fiter)
        
        # if any conversation already exist, fetch the history and return
        if conversation.exists():
            print("conversation found")
            serializer = self.serializer_class(conversation[0])
            
        
        # if no conversation exists, create new conversation
        else:
            conversation = Conversation.objects.create(initiator=request.user, reciever=participant)
            
            # serialize
            serializer = self.serializer_class(conversation)
        
        return Response(serializer.data, status=201)