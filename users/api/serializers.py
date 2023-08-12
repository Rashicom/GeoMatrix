from .models import CustomUser
from rest_framework import serializers


class Custom_user_serializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id','first_name','last_name','email','adhar_id','contact_number','social_rank','password',]


class Login_serializer_user(serializers.Serializer):

    email = serializers.EmailField(required = True)
    password = serializers.CharField(required = True)