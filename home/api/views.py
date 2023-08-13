from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from .serializers import main_section_serializer, main_section_serializer_get, about_section_serializer, product_section_serializer, service_section_serializer
from .models import main_section, main_section_images, main_section_descriptions, about_section, product_section, service_section
from django.db import transaction


class main_section_data(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = main_section_serializer

    @transaction.atomic
    def post(self, request, format=None):
        """
        this function is accepting the all filds of the given serializer and save the 
        details in the respective tables. 2 table is refered by a primary table. 
        returns created data, return image will be null(returning file make long repsponse time), but saved
        """

        # serializing and validating data
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):

            try:
                main_section_instance = main_section(title = serializer.validated_data.get('title'))
                main_section_instance.save()

                main_section_images_instance = main_section_images(main_section = main_section_instance, image = serializer.validated_data.get('image'))
                main_section_images_instance.save()

                main_section_descriptions_instance = main_section_descriptions(main_section = main_section_instance, description = serializer.validated_data.get('description'))
                main_section_descriptions_instance.save()
            except Exception as e:
                print(e)
                return Response({"details": "somthing went wron"}, status=500)
            
            return Response(serializer.data, status=201)
    
    def get(self, request, format=None):
        """
        returning the data
        """
        main_section_instance = main_section.objects.all().first()
        images = main_section_images.objects.all()
        descriptions = main_section_descriptions.objects.all()
        
        # fetching data, image and descriptions are contains list of elements
        # so populating all elements to array to serialize and return
        serialized_data = {
            "title":main_section_instance.title,
            "image":[img.image for img in images],
            "description":[desc.description for desc in descriptions]
        }

        serializer = main_section_serializer_get(serialized_data)
        return Response(serializer.data, status=201)



class about_section_data(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = about_section_serializer

    def post(self, request, format=True):
        """
        only accesses by authenticated admin user
        this function accepting the datas mentioned in the about_section_serializer
        and update the database then return the created data as response
        """
        
        # serializing data, validating and save
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # return updated data as response
        return Response(serializer.data, status=200)
    
    def get(self, request, format=True):
        """
        anyone can access this function.
        this fucntion returning about_section_serializer data for all users
        """
        serializer = self.serializer_class(about_section.objects.all().first())
        return Response(serializer.data, status=200)


class product_section_data(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = product_section_serializer

    def post(self, request, format=True):
        """
        only accesses by authenticated admin user
        this function accepting the datas mentioned in the product_section_serializer
        and update the database then return the created data as response
        """
        
        # serializing data, validating and save
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # return updated data as response
        return Response(serializer.data, status=200)
    
    def get(self, request, format=True):
        """
        anyone can access this function.
        this fucntion returning product_section_serializer data for all users
        """
        serializer = self.serializer_class(product_section.objects.all().first())
        return Response(serializer.data, status=200)



class service_section_data(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = service_section_serializer

    def post(self, request, format=True):
        """
        only accesses by authenticated admin user
        this function accepting the datas mentioned in the service_section_serializer
        and update the database then return the created data as response
        """
        
        # serializing data, validating and save
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # return updated data as response
        return Response(serializer.data, status=200)
    
    def get(self, request, format=True):
        """
        anyone can access this function.
        this fucntion returning service_section_serializer data for all users
        """
        serializer = self.serializer_class(service_section.objects.all().first())
        return Response(serializer.data, status=200)