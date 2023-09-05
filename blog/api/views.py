from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny,IsAuthenticated
from .customauth import GovuserJwtAuthentication
# Create your views here.


class test(APIView):

    authentication_classes = [GovuserJwtAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        print("test view")
        print(request.auth)
        print(request.user)
        return Response({"details":"test response"},status=200)




