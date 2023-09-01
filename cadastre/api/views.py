from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Land, NormalUser, LandGeography, LandOwnershipRegistry
from .serializers import LandRegistraionSerailizer,LandOwnershipRegistrySerializer ,LandSerializer, LandGeographySerializer, ChangeOwnershipRegistrySerializer, LandDataResponseSerializer, LandSplitSerializer
from .landoperations import LandSplitValidator, LandRegistration
from django.contrib.gis.geos import Point, Polygon
from django.contrib.gis.db.models.functions import Area
from django.db import transaction
from geopy.geocoders import Nominatim
from django.contrib.gis.geos import GEOSGeometry
import pandas as pd
import json
from pyproj import Geod
from shapely import wkt


"""/////////////////GOV USER///////////////////////"""


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

        # AREA CALCULATION
        # specify a named ellipsoid(earth shape)
        geod = Geod(ellps="WGS84")

        # landpoligon.wkt returns wkt(well known test) string like format
        # wkt.load is converting the string representation of polygon in to polygon
        poly = wkt.loads(boundary_polygon.wkt)

        # geometry_area_perimeter returning two valurs area in m^2 and the perimeter
        # we take the area by specifing [0]
        # area my be +ve or -ve , depending on clockwise or anticlockwise direction we drow the polygon
        # to get posive area always we take the abs value
        area = abs(geod.geometry_area_perimeter(poly)[0])

        # taking only 2 decimal value
        area = round(area, 2)

        # update tables
        try:
            with transaction.atomic():

                # updating land table
                land_serializer = LandSerializer(data=request.data)
                land_serializer.is_valid(raise_exception=True)
                land_instance = land_serializer.save(user=user_instance)
                print("land table updated")
                
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
                land_geography_serializer.save(land=land_instance)

        except Exception as e:
            print(e)
            return Response({"details":"somthing went wrong"})


        print("area", area)

        print(boundary_polygon)
        print(location_coordinate)
        
        return Response(serializer.data,status=201)



# land bulk registration from exl file for a perticular user
class BulkRegisterLand(APIView):
    
    serializer_class = LandRegistraionSerailizer
    def post(self, request, format=None):
        """
        fetching data from the exl file and validate all the rows before
        updating to the data base.
        WARNING: reading rows from the exl file and updating to data base is rise many probloms
                 may be some rows contain fault information and the updation cancelled
                 so we have to make sure all filds of all rows are valied before update
        we have a some stup to follow the bulc creation
        1- first for loop: iterate through rows and validate all rows
        2- second for loop: iterate through rows and update to database
        """

        email = request.data.get("email")
        user_instance = NormalUser.objects.get(email=email)

        # geting the exl file
        land_exl_file = request.FILES.get("landfile")

        # if the file not found return error
        if not land_exl_file:
            return Response({"details":"file not provided"}, status=403)
        
        # process the exl file usign pandas
        reader = pd.read_excel(land_exl_file)
        
        # first iteration for  validating all data
        for row in reader.itertuples():
            """
            creating a data object for serialize it and validate
            return if any exception found
            """

            # TEST 1 - serialize and validate
            data = {
                "email": email,
                "locality": row.locality,
                "district": row.district,
                "state": row.state,
                "zip_code": row.zip_code,
                "land_type": row.land_type,
                "boundary_polygon": json.loads(row.boundary_polygon)
            }
            
            serializer = self.serializer_class(data=data)
            serializer.is_valid(raise_exception=True)


            # TEST 2 - making poligon to test cordinates are following polygon rules
            boundery_coordinates = data.get('boundary_polygon')
            boundery_coordinates.append(boundery_coordinates[0])
            
            try:
                land_poligon = Polygon(boundery_coordinates,srid = 4326)
                print("polygon DONE")
            except Exception as e:
                print(e)
                return Response({"details":"Polygon creation filed. please check the coordinates", "failed_row":row.Index+1, "coordinates":row.boundary_polygon},status=422)
            
            # TEST 3 - address and coordinates cross match using geopy
            # test pending

            # TEST 4 - poligon overlaping check
            # test pending
        
        print("PRIMARY VALIDATION FILE CKECK COMPLETED SUCCESSFULLY")

        # every updation loop data is appended to the response data to return data back to the user
        response_data = []

        # after a successful validation the file is readyu to update
        # update to database
        for row in reader.itertuples():

            # create a data object for each row
            data = {
                "email": email,
                "locality": row.locality,
                "district": row.district,
                "state": row.state,
                "zip_code": row.zip_code,
                "land_type": row.land_type,
                "boundary_polygon": json.loads(row.boundary_polygon)
            }

            # make closed coordinates to create polygon
            boundery_coordinates = data.get('boundary_polygon')
            boundery_coordinates.append(boundery_coordinates[0])

            # creat poligon
            land_poligon = Polygon(boundery_coordinates,srid = 4326)

            # generate a centroid for the poligon for update the land location_cordinates of the LangGeography table
            location_coordinate = land_poligon.centroid

            # calculating area enclosed by the polygon
            # this area is in squre degree, so we have to find the area in sqr meter
            
            # AREA CALCULATION
            # specify a named ellipsoid(earth shape)
            geod = Geod(ellps="WGS84")

            # landpoligon.wkt returns wkt(well known test) string like format
            # wkt.load is converting the string representation of polygon in to polygon
            poly = wkt.loads(land_poligon.wkt)
            
            # geometry_area_perimeter returning two valurs area in m^2 and the perimeter
            # we take the area by specifing [0]
            # area my be +ve or -ve , depending on clockwise or anticlockwise direction we drow the polygon
            # to get posive area always we take the abs value
            area = abs(geod.geometry_area_perimeter(poly)[0])

            # taking only 2 decimal value
            area = round(area, 2)

            print("area",area)
            # table updation
            try:
                with transaction.atomic():

                    # updating land table
                    land_serializer = LandSerializer(data=data)
                    land_serializer.is_valid(raise_exception=True)
                    land_instance = land_serializer.save(user=user_instance)
                    print("land table updated")

                    # update land registry
                    land_ownership_serializer = LandOwnershipRegistrySerializer(data={"user":user_instance.id, "land":land_instance.land_number})
                    land_ownership_serializer.is_valid(raise_exception=True)
                    land_ownership_serializer.save()
                    print("land ownership table updated")

                    # save land geography table
                    land_data = {
                        "land":land_instance.land_number,
                        "land_type":row.land_type,
                        "location_coordinate":location_coordinate,
                        "boundary_polygon":land_poligon,
                        "area":area
                    }

                    land_geography_serializer = LandGeographySerializer(data=land_data)
                    land_geography_serializer.is_valid(raise_exception=True)
                    land_geography_serializer.save(land=land_instance)

            except Exception as e:
                print(e)
                return Response({"detailes":"database updation filed"}, status=500)

            # creating response data object and append to to response
            response_data.append(land_data)

        # serializing response data and return
        response_serializer = LandDataResponseSerializer(response_data,many=True)
        return Response(response_serializer.data,status=201)


class LandSplitRegistration(APIView):

    serializer_class = LandSplitSerializer

    def post(self, request, format=None):
        """
        this method accepting a parent lands user email, land number, and a exl file 
        the exl file is used to specify
        1 - fetch data and validate user is the owner of the specified land
        2 - validate file data
        3 - register land
        4 - after a sucessfull land registration set parent land is_active = Fasle and active_till = today date
        """

        # geting the exl file
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # checking the user and land is exist in the database   
        try:
            parent_user_instance = NormalUser.objects.get(email=serializer.validated_data.get("parent_user_email"))
        except Exception as e:
            return Response({"details":"parent user not found"}, status=404)
        
        try:
            parent_land_instance = Land.objects.get(land_number=serializer.validated_data.get("parent_land_number"))
        except Exception as e:
            return Response({"details":"parent land not found"}, status=404)
        
        
        # check the owner of the land is the same
        if parent_land_instance.user != parent_user_instance:
            return Response({"details":"land owner and specified user not match"},status=422)


        # validating file data before create it
        land_record_file = request.FILES.get("land_record_file")
        land_validator = LandSplitValidator(land_record_file=land_record_file,parent_land_instance=parent_land_instance)

        # validating land_record_file
        # if any exception found response returned explicitly
        land_validator.is_valied()

        # proceed to update database
        register = LandRegistration()
        response_data = register.RegisterMultipleLandForMultipleUser(land_record_file,parent_land=parent_land_instance)
        if response_data is None:
            return Response({"details":"somthing went wrong"})
        
        print(response_data)

        return Response(response_data,status=200)

            




# change land ownership
class ChangeLandOwnership(APIView):

    serializer_class = ChangeOwnershipRegistrySerializer

    def post(self, request, format=None):
        """
        accepts enough information to change the ownership of a land to new owner
        change owner field in the land tabele and add new owner to the registry to keep track the registrations
        """
        
        # serializing and vaidating data
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # get new user and land instance instance
        try:
            new_user_instance = NormalUser.objects.get(email=serializer.validated_data.get("new_owner_email"))
        except Exception as e:
            print(e)
            return Response({"details":"user not found"}, status=404)
        
        try:
            land_instance = Land.objects.get(land_number=serializer.validated_data.get("land_number"))
        except Exception as e:
            print(e)
            return Response({"details":"land not found"}, status=404)

            
        # update tables
        try:
            with transaction.atomic():

                # updating land table user to new owner user
                land_instance.user = new_user_instance
                land_instance.save()

                # add new user to land registry to keeptrck of land registration
                LandOwnershipRegistry.objects.create(user=new_user_instance, land=land_instance)

        except Exception as e:
            print(e)
            return Response({"details":"somthing went wrong"}, status=500)

        # return new land detals
        land_details = {
            "land_number":land_instance.land_number,
            "new_user":serializer.validated_data.get("new_owner_email"),
        }
        return Response(land_details, status=201)



    

# get land by land_id 
class GetLand(APIView):

    serializer_class = LandGeographySerializer
    # custom admin auth must be given here
    def get(self, request, format=None):
        """
        this is accepting a parameter land_id. and return back the perticular land info
        if the land_id not provided all the land info returned
        """

        # get parameter
        land_number = request.query_params.get('land_number')
        
        # fetching data according to the parameter.
        # if land_no provided, return specific land. if lan_no not provided, return all lands
        if land_number:
            
            land_record = LandGeography.objects.get(land__land_number=land_number, land__is_active=True)
            serializer = self.serializer_class(land_record)
        
        else:

            land_record = LandGeography.objects.all()
            serializer = self.serializer_class(land_record,many=True)
        
        # usign GEOSGeometry we can change the cordinates to many format
        # now row queryset from database returned
        # print(GEOSGeometry(lnd).geojson)

        return Response(serializer.data,status=200)



# timelayered land
# active lands in a specific time and date
# helps to see the changes, and land division rate over time


"""/////////////////GOV USER///////////////////////"""

class GetUserLand(APIView):
    serializer_class = LandGeographySerializer

    def get(self, request, format=None):
        
        # get email from parameter
        email = request.query_params.get('email')
        if not email:
            return Response({"email":"this paremeter is required"})
        
        # get user instance
        try:
            user = NormalUser.objects.get(email=email)
        except Exception as e:
            print(e)
            return Response({"details":"user not found"},status=401)
        
        # fetchind data and serialize it
        user_land_list = LandGeography.objects.filter(land__user=user, land__is_active=True)
        serializer = self.serializer_class(user_land_list, many=True)

        return Response(serializer.data, status=200)



class GetFilteredLand(APIView):

    serializer_class = LandGeographySerializer

    def get(self, request, format=None):
        """
        this function is filtering based on land_type
        """
        pass