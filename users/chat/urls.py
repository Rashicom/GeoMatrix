from django.urls import path, include
from . import views

urlpatterns = [
    path("start_chat/", views.StartConversation.as_view()),
        
    
    ]