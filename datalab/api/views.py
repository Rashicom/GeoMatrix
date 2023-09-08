from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
# Create your views here.





# test response for nginex call
class test(APIView):
    
    def get(self, request, format=None):
        return Response({"details":"datalab is responding"}, status=200)

