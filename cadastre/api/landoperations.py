from .models import NormalUser, Land, LandOwnershipRegistry, LandGeography
from .serializers import LandRegistraionSerailizer, LandSerializer, LandOwnershipRegistrySerializer, LandGeographySerializer, LandDataResponseSerializer, LandRegistrationMultipleUsers
from rest_framework.response import Response
from django.contrib.gis.geos import Point, Polygon
from rest_framework.exceptions import ValidationError,NotFound
from django.db import transaction
import pandas as pd
import json
from pyproj import Geod
from shapely import wkt

# registration and validation

class LandRegistration:

    def __init__(self):
        pass


    def RegisterMultipleLand(self):
        """
        accepting a exl file with multiple land records and update data base
        good for register multiple land for single user
        """

        pass


    def RegisterMultipleLandForMultipleUser(self,land_record,parent_land=None):
        """
        accepting a exl file with multiple land records with specific user
        and register land for the specific user
        good for land registration for multiple users after land split
        1 - basic validation on arguments
        2 - reading file using pandas
        3 - looping through rows and update database
            every iteration created land record row pushed to a response_data list to return
        4 - returning a list of land records which is successfully created

        WARNING: This method not performing any validation on the exl file.
                 The file must be validated before calling this function.
                 
        """

        # process the exl file usign pandas
        reader = pd.read_excel(land_record)
        
        # initializing a response_land_record list, every iteration created land object is append to the list
        response_land_record = []

        # iterating throgh rows to fetch each land land data and update
        for row in reader.itertuples():
            """
            creating a data object for serialize it and validate
            return if any exception found
            """

            # creating data object for each row
            data = {
                "email": row.owner_email,
                "locality": row.locality,
                "district": row.district,
                "state": row.state,
                "zip_code": row.zip_code,
                "land_type": row.land_type,
                "boundary_polygon": json.loads(row.boundary_polygon)
            }

            # serializing data and validating
            serializer = LandRegistraionSerailizer(data=data)
            serializer.is_valid(raise_exception=True)

            # register land
            land_data = self.RegisterLand(serializer.validated_data,parent_land=parent_land)
            response_land_record.append(land_data)
            print("land record created")
            print(response_land_record)
        
        # serializing response data and return
        response_serializer = LandDataResponseSerializer(response_land_record,many=True)
        return response_serializer.data


    def RegisterLand(self, validated_data, parent_land=None):
        """
        registering single land for a perticular user
        """
        email = validated_data.get("email")

        # fetching user instance
        try:
            user_instance = NormalUser.objects.get(email=email)
        except Exception as e:
            print("user not found")

            # this implicitly return error response
            raise NotFound("user not found")
        
        # first cordinate append to the last to make a closed loop to obay the poligon pricliple.
        boundery_coordinates = validated_data.get('boundary_polygon')
        boundery_coordinates.append(boundery_coordinates[0])

        # creating poligon
        try:
            land_poligon = Polygon(boundery_coordinates,srid = 4326)
            print("polygon DONE")
        except Exception as e:
            print(e)

            # implicitly return response
            raise ValidationError("Polygon creation filed. please check the coordinates")

        # generate a centroid for the poligon for update the land location_cordinates of the LangGeography table
        location_coordinate = land_poligon.centroid

        # get area of poligon
        area = self.LandArea(land_polygon=land_poligon)

        # update table
        try:
            with transaction.atomic():
                # updating land table
                land_serializer = LandSerializer(data=validated_data)
                land_serializer.is_valid(raise_exception=True)

                # if the parent_land argunet is recived it means the land is splited from a parent land
                # so set parent_land_id forign key =  parent_land while savind
                if parent_land:
                    land_instance = land_serializer.save(user=user_instance, parent_land_id=parent_land)
                
                # else normal creation
                else:
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
                    "land_type":validated_data.get("land_type"),
                    "location_coordinate":location_coordinate,
                    "boundary_polygon":land_poligon,
                    "area":area
                }

                land_geography_serializer = LandGeographySerializer(data=land_data)
                land_geography_serializer.is_valid(raise_exception=True)
                land_geography_serializer.save(land=land_instance)

        except Exception as e:
            print("table updation filed")
            return None

        return land_data



    def LandArea(sef,land_polygon=None):
        """
        accepting a poligon and returnint its area in m^2 as floot
        """
        if not land_polygon:
            return None
        
        # AREA CALCULATION
        # specify a named ellipsoid(earth shape)
        geod = Geod(ellps="WGS84")

        # landpoligon.wkt returns wkt(well known test) string like format
        # wkt.load is converting the string representation of polygon in to polygon
        poly = wkt.loads(land_polygon.wkt)

        # geometry_area_perimeter returning two valurs area in m^2 and the perimeter
        # we take the area by specifing [0]
        # area my be +ve or -ve , depending on clockwise or anticlockwise direction we drow the polygon
        # to get posive area always we take the abs value
        area = abs(geod.geometry_area_perimeter(poly)[0])

        # taking only 2 decimal value
        area = round(area, 2)
        return area
        





# for different kinds of land validation
# inherit this class for create land validators
class BaseLandValidator:

    def __init__(self, land_record_file=None):
        self.land_record_file = land_record_file
        
    
    def is_valied(self):
        pass  


# this class is inheriting the baseLandValidator class
class LandSplitValidator(BaseLandValidator):
    """
    parameters: land_record_file and parent_user_instance
    """

    def __init__(self, land_record_file=None, parent_land_instance=None):
        super().__init__(land_record_file=land_record_file)


    def is_valied(self):
        """
        this method is accepting a land_record_file. and iterating through
        row of the file and perform different kinds of validations on each row      
        
        raise_excaption=True: return response implicitly if exception found
        raise_exceprion=False: return True if file is valied else False
        """
        land_record_file = pd.read_excel(self.land_record_file)

        # iterate through rows to perform validation in each row
        for row in land_record_file.itertuples():
        # performing different validation on the row

            data = {
                "locality":row.locality,
                "district":row.district,
                "state":row.state,
                "zip_code":row.zip_code,
                "land_type":row.land_type,
                "owner_email":row.owner_email,
                "boundary_polygon":json.loads(row.boundary_polygon)
            }

            # serializign data and validating
            serializer = LandRegistrationMultipleUsers(data=data)
            
            # CHEKCING 1
            serializer.is_valid(raise_exception=True)

            
            # CHECKING 2 owner user is exist or not
            try:
                NormalUser.objects.get(email=serializer.validated_data.get("owner_email"))
            except Exception as e:
                print(e)
                # returnign error response implicitly
                
                raise NotFound("chiled owner user not found")


            # CHECKING 3
            # test polygon is valied or not
            # this return exception if failed to create a polygon from given cordinates
            self.is_valied_polygon(boundery_coordinates=json.loads(row.boundary_polygon))   
        
        return True




    def is_valied_polygon(self,boundery_coordinates=None):
        """
        checking the cordinates can form a polygon or not
        returning bool reponse
        """

        # forming a closed coordinates
        boundery_coordinates.append(boundery_coordinates[0])

        try:
            land_polygon = Polygon(boundery_coordinates,srid=4326)
        except Exception as e:
            raise ValidationError("cant make a polygon from the given coordinates, please check the coordinates")





    # this fuction only visible to the inherited classes
    def create_polygon(boundery_coordinates=None):
        """
        accepting a coordinates and validate the poligon is valied or not
        return polygon if it is valied otherwise rise exception
        """
        pass




