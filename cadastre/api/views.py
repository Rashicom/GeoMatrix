from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Land, NormalUser
from .serializers import LandRegistraionSerailizer,LandOwnershipRegistrySerializer ,LandSerializer, LandGeographySerializer
from django.contrib.gis.geos import Point, Polygon
from django.contrib.gis.db.models.functions import Area
from django.db import transaction


# regisering a new land
class RegisterLand(APIView):
    authentication_classes = [JWTStatelessUserAuthentication]
    permission_classes = [AllowAny]
    serializer_class = LandRegistraionSerailizer

    def post(self, request, format=None):
        """
        registering a cadester involve many different tests and updations
        data and specified location need to be cross checked to find the cordinates are in the place or not
        1 - cross matching place vs provided cordinates
        2 - valify the poligon and convert to a poligon
        3 - make a point_lacation data which is the mid cordinates of created poligon
        4 - test the poligon is already overlaping any of other poligon which is exist in database
        5 - update tables
        """

        # validatting data
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # fetching user instance
        user_instance = NormalUser.objects.get(email=serializer.validated_data.get("email"))
        
        # validating poligon
        boundary_coordinates = serializer.validated_data.get("boundary_polygon")

        # a poligon must have 3 corditates to make a loop
        if len(boundary_coordinates) < 4:
            print("invalied poligon")
        
        """
        user return some cordinates which minimum or 3 cordinates. by joing the 
        3 cordinates we get a curved line not a closed loop. its not cusidered as a poligon
        a poligon must be a closed one
        so we have to connect last cordinate to the first corditate to form a cadestre as well as a polygon
        """

        # adding first cordinate to the last to form a polygon(closed border)
        boundary_coordinates.append(boundary_coordinates[0])

        # creating a polygon
        # try to crete a polygon, if creatin a poligon faild, return error response
        try:
            """
            cordinates should be follow the plygon rules to form a polygon
            otherwise it rises exceptions, and exception block catch it and return error response
            """
            boundary_polygon = Polygon(boundary_coordinates,srid = 4326)
        except Exception as e:
            print(e)
            error = {"details":"cant create a polygon using given cordinates, pleace enter correct coordinates"}
            return Response(error,status=200)
        
        # generate a centroid for the poligon for update the land location_cordinates of the LangGeography table
        location_coordinate = boundary_polygon.centroid

        # calculating area enclosed by the polygon
        # this area is in squre degree
        area = boundary_polygon.area

        # update tables
        try:
            with transaction.atomic():

                # updating land table
                land_serializer = LandSerializer(data=request.data)
                land_serializer.is_valid(raise_exception=True)
                land_instance = land_serializer.save(user=user_instance)
                print("land table updated")
                print(land_instance)
                
                # update land registry
                land_ownership_serializer = LandOwnershipRegistrySerializer(data={"user":user_instance.id, "land":land_instance.land_number})
                land_ownership_serializer.is_valid(raise_exception=True)
                land_ownership_serializer.save()
                print("land ownership table updated")

                # save land geography table
                land_data = {
                    "land":land_instance.land_number,
                    "land_type":serializer.validated_data.get("land_type"),
                    "location_coordinate":location_coordinate,
                    "boundary_polygon":boundary_polygon,
                    "area":area
                }

                land_geography_serializer = LandGeographySerializer(data=land_data)
                land_geography_serializer.is_valid(raise_exception=True)
                land_geography_serializer.save()

        except Exception as e:
            print(e)
            return Response({"details":"somthing went wrong"})


        print("area", area)

        print(boundary_polygon)
        print(location_coordinate)
        
        return Response(serializer.data,status=201)