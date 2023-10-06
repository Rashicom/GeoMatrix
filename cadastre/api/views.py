from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTStatelessUserAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Land, NormalUser, LandGeography, LandOwnershipRegistry, LandTypeTaxList, TaxInvoice
from .serializers import LandRegistraionSerailizer,LandOwnershipRegistrySerializer ,LandSerializer, LandGeographySerializer, ChangeOwnershipRegistrySerializer, LandDataResponseSerializer, LandSplitSerializer, LandTypeTaxListSerializer, TaxInvoiceSerializer, DateFilteredLandSerializer, LandInAddressSerializer
from .landoperations import LandSplitValidator, LandRegistration
from .landtax import LandTax
from .landfilters import BaseLandFilters
from .customauth import GovuserJwtAuthentication
from django.contrib.gis.geos import Point, Polygon
from django.contrib.gis.db.models.functions import Area
from django.db import transaction
from geopy.geocoders import Nominatim
from django.contrib.gis.geos import GEOSGeometry
from rest_framework.decorators import action
import pandas as pd
import json
from pyproj import Geod
from shapely import wkt
from datetime import date


"""/////////////////GOV USER///////////////////////"""


# regisering a new land
class RegisterLand(APIView):
    authentication_classes = [GovuserJwtAuthentication]
    permission_classes = [IsAuthenticated]
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
            return Response({"details":"invalied cordinates"},status=400)

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
            return Response(error,status=400)
        
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
            return Response({"details":"somthing went wrong"},status=500)


        print("area", area)

        print(boundary_polygon)
        print(location_coordinate)
        
        return Response(serializer.data,status=201)



# land bulk registration from exl file for a perticular user
class BulkRegisterLand(APIView):
    
    authentication_classes = [GovuserJwtAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = LandRegistraionSerailizer

    def post(self, request, format=None):
        """
        fetching data from the exl file and validate all the rows before
        updating to the data base.
        WARNING: reading rows from the exl file and updating to data base is rise many probloms
                 may be some rows contain fault information and the updation cancelled
                 so we have to make sure all filds of all rows are valied before update
        we have a some stup to follow the bulc creation
        1- first for loop: iterate through rows and validate data
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

    authentication_classes = [GovuserJwtAuthentication]
    permission_classes = [IsAuthenticated]
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
            return Response({"details":"somthing went wrong"},status=500)
        
        # after a succsessfull land registration, make some changes in the parent land, becouse parent land must be removed from some checks like taxing, filtering , etc..
        # the parent land will have some child lands which is splited from parent, and the spliting info we need to store for data generations so we cant delete
        # set is_ctive=True and active_till = today date
        parent_land_instance.is_active=False
        parent_land_instance.active_till=date.today()
        parent_land_instance.save()

        return Response(response_data,status=201)

            


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

    authentication_classes = [GovuserJwtAuthentication]
    permission_classes = [IsAuthenticated]
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


# land tax crud 
class LandTaxRates(APIView):
    
    authentication_classes = [GovuserJwtAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = LandTypeTaxListSerializer

    def post(self, request, format=None):
        """
        this fuction expecting land_type and land_tax
        and update.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data,status=201)


    def get(self, request, format=None):
        """
        accept : land_type, return land tax of given land_type
        if no land type return all land_type tax list
        this method is returning the tax list
        """
        land_type = request.query_params.get("land_type")
        
        # if the user enter for a specific landtype tax
        if land_type:
            
            # if land_type does not exist return error message
            try:
                tax = LandTypeTaxList.objects.get(land_type=land_type)
            except Exception as e:
                return Response({"details":"land_type does not exist"}, status=400)

            serializer = self.serializer_class(tax)
            return Response(serializer.data, status=200)

        # else return tax list
        else:            
            tax_list = LandTypeTaxList.objects.all()
            serializer = self.serializer_class(tax_list, many=True)
            return Response(serializer.data, status=200)



class GenerateTaxInvoice(APIView):

    authentication_classes = [GovuserJwtAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = TaxInvoiceSerializer
    
    # get active invoice
    def get(self, request, format=None):
        """
        get alll active invoices
        """
        invoice_list = TaxInvoice.objects.filter(is_active=True)
        serializer = self.serializer_class(invoice_list,many=True)
        return Response(serializer.data, status=200)

    # generate invoice
    def post(self, request, format=None):
        """
        this fuction iterate through the land model objects to generate land tax
        checking the land objects last tax invoice generated date. if the defference with tody grater than 30 or any specific period generate a new invoice
        if there is no last invoice found, its a new land registered, and check the land registered date and generate invoice if grater than 30 or any specific periods
        """
        
        # returned created invoice push to this list to return as api response
        response_invoices = []

        # iterating through active land model
        for land_obj in Land.objects.filter(is_active=True):
            
            # checke the lands last generated tax invoice date
            # last invoice matching for the perticular land
            invoice_instance = TaxInvoice.objects.filter(land=land_obj).last()
            
            # if there is a invoice found, it checks again if the invoice validity is over.
            # if it over we have to generate new invoice fot the next period
            if invoice_instance:

                # checking the dates if the difference is grater or egual to th specifide period
                if (date.today() - invoice_instance.tax_date).days >= 7:
                    """
                    now the difference is grate than the specific period
                    generate new tax invoice for the next period
                    """
                    # returning invoice instance if created ontherwise error message returned
                    invoice = LandTax(land_instance=land_obj)
                    response_invoices.append(invoice)

            # if no last invoice is found, it means its a newly registered land
            # procede to make a first invoice if time period is passes
            else:
                """
                now today date is checking against the registration date of the land
                if the difference grater than of the specific date, time generate a new invoice
                """
                if (date.today() - land_obj.active_from).days >= 1:

                    # returning invoice instance if created ontherwise error message returned
                    invoice = LandTax(land_instance=land_obj,new_land=True)
                    invoice_instance = invoice.generate_tax_invoice()
                    response_invoices.append(invoice_instance)
                else:
                    print("no taxable lands found")
        serializer = self.serializer_class(response_invoices, many=True)
        return Response(serializer.data, status=201)



# FILTER : time layer snapshort
class LandFilteres(viewsets.ViewSet):

    serializer_class = DateFilteredLandSerializer

    # deail=true means it called on get, for other http methods, set it to true then pass extra argument called methods=[post,put]
    @action(detail=False)
    def time_snapshort(self, request, format=None):
        """
        accepts : snapshort as a params
        return : time snapshort lands details 
        """
        
        # geting snapshort date from params
        snapshort_date = request.query_params.get("snapshort_date")
        if not snapshort_date:
            return Response({"details":"snapshort_date not provided"},status=400)

        # creating object fo base aldn filter class
        # all the filters in this class returning filtered objects as Land model query set
        land_filter = BaseLandFilters()

        # time layer filter
        filtered_data = land_filter.timelayer_snapshort(snapshort_date=snapshort_date)
        
        # serializing and returning data
        serializer = self.serializer_class(filtered_data, many=True)
        return Response(serializer.data,status=200, )


    @action(detail=False)
    def land_in_address(self, request, format=None):
        """
        accept: state,district,locality,zipcode,active_land_only for query params
        all fieds are optional
        active_land_only = True by default(retunrs only active lands)
        return: filtering the land according to the given data and return filtered data
        """

        # fetchind date from params and serialize it
        land_in_address_serializer = LandInAddressSerializer(data=request.query_params)
        land_in_address_serializer.is_valid(raise_exception=True)

        # creating object fo base aldn filter class
        # all the filters in this class returning filtered objects as Land model query set
        land_filter = BaseLandFilters()

        # address filter
        filtered_data = land_filter.land_in_address(
            state=land_in_address_serializer.validated_data.get("state"),
            district=land_in_address_serializer.validated_data.get("district"),
            locality=land_in_address_serializer.validated_data.get("locality"),
            zip_code=land_in_address_serializer.validated_data.get("zip_code"),
            active_land_only=land_in_address_serializer.validated_data.get("active_land_only")
        )
        
        #serializing and returning data
        serializer = self.serializer_class(filtered_data, many=True)
        return Response(serializer.data,status=200)

    
    @action(detail=False)
    def land_type(self, request, format=None):
        """
        accept: land_type_list list()
        returns: filtering land according to the value contained in the list
        """

        land_type_list = request.query_params.get("land_type_list")
        
        # creating object fo base aldn filter class
        # all the filters in this class returning filtered objects as Land model query set
        land_filter = BaseLandFilters()
        filtered_data = land_filter.land_type_filter(land_type_list=json.loads(land_type_list))

        # serialize and return
        serializer = self.serializer_class(filtered_data,many=True)
        return Response(serializer.data, status=200)





"""/////////////////NORMAL USER///////////////////////"""

class GetUserLand(APIView):
    serializer_class = LandGeographySerializer

    def get(self, request, format=None):
        """
        return land details of the requested authenticated user
        """
        # get user
        user = request.user
        
        # fetchind data and serialize it
        user_land_list = LandGeography.objects.filter(land__user=user, land__is_active=True)
        serializer = self.serializer_class(user_land_list, many=True)

        return Response(serializer.data, status=200)






class test(APIView):
    authentication_classes = [GovuserJwtAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        print("accessed")
        return Response({"details":"cadestre microservice responding.."})