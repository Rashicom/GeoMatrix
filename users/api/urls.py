from django.urls import path, include
from . import views

urlpatterns = [
    path('signup/',views.signup.as_view()),
    path('login/',views.login.as_view()),
    path('add_address/', views.add_address.as_view()),
    path('edit_address/',views.edit_address.as_view()),
    

]