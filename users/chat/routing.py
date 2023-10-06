from django.urls import re_path

from . import consumer

# socket connection url expecting a room as a uuid named room_name
# room_name can be found from scope > url_route > kwargs > room_name
websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>[\w-]+)/$", consumer.ChatConsumer.as_asgi()),
    
]