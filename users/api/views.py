from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import authenticate
from .serializers import Custom_user_serializer, Login_serializer_user, Address_serializer
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Wallet, Address


# Create your views here.

# user creation
class signup(APIView):
    permission_classes = [AllowAny]
    serializer_class = Custom_user_serializer

    def post(self, request, format=None):
        """
        creating useer, recieving request.data and serialzing it, then
        if validated create new user return a newly generated jwt access and refresh tocken
        """
        print("request hit")
        # serializing request.data
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            """
            if the data is validated password is hashed and creating new user.
            retunt with generated jwt tocken
            """

            # creating user and and set password, save() doesnt hash password
            hashed_password = make_password(serializer.validated_data['password'])
            user = serializer.save(password = hashed_password)
            
            # excluding password from the response and send response
            response_data = serializer.data

            # updating wallet table
            new_wallet = Wallet(user = user)
            new_wallet.save()

            # removing password from response and send response
            response_data.pop('password')
            print("user created")
            return Response(response_data,status=201)
            

# login
# login
class login(APIView):

    serializer_class = Login_serializer_user
    permission_classes = [AllowAny]

    def post(self, reuqest, format=None):
        """
        validating the user credencials and generating access and regresh
        jwt tocken if the user is validated otherwise return error message
        """
        print("request hit")
        # serializing data
        seriazed_data = self.serializer_class(data=reuqest.data)

        # validating credencians, if credencials invalied error message
        # automatically send to frond end
        if seriazed_data.is_valid(raise_exception=True):
            
            # fetching credencials for validation
            email = seriazed_data.validated_data['email']
            password = seriazed_data.validated_data['password']

            # authenticate func returns user instence if authenticated
            user = authenticate(email = email, password = password)

            # if user is authenticated generate jwt
            if user is not None:
                
                print("login success")
                # generating jwt tocken
                refresh = RefreshToken.for_user(user)
                access = refresh.access_token
                
                # returning response with access and refresh tocken
                # refresh tocken used to generate new tocken before tockens session expired
                return Response(          
                    {
                        "email":email,
                        "password":password,
                        "access":str(access),
                        "refresh":str(refresh)
                    },
                    status=201     
                )
            
            # if user none, wrong email or passord
            else:
                return Response({"details":"wrong email or password"}, status=401)



# update address table
class add_address(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = Address_serializer

    def post(self, request, format=None):
        """
        this function is expecting all address fields and create
        a new address for the user who authenticated and return the 
        created address as a response
        """

        # fetching data
        user = request.user
        serializer = self.serializer_class(data=request.data)

        # validating data, if exception found, message automaticaly send to the frond end
        if serializer.is_valid(raise_exception=True):
            """
            creating a new address for the user who is authenticated 
            and save it and return the created address as a resoponse
            
            if any exception found whicle calling is_valied, the exception send back
            implicitly, becouse raise_exception set to true
            """

            try:
                serializer.save(user = user)
            except Exception as e:
                print(e)
                return Response({"details":"somthing went wrong"}, status=400)
            return Response(serializer.data, status=201)



# edit address
# edit address
class edit_address(APIView):

    permission_classes=[IsAuthenticated]
    serializer_class = Address_serializer

    def patch(self, request, format=None):
        """
        updating user address details
        """
        address_instence = Address.objects.get(user = request.user)
        # serializing data
        serialized_data = self.serializer_class(address_instence,data = request.data, partial=True)
        
        # validating serialized data
        # if any exception found exception implicitly send back to frondend
        # raise_exception responsible for implicit return
        if serialized_data.is_valid(raise_exception=True):
            """
            serializer model class Address have one forign key.
            if the user wants to update the state or country we have to fetch the insance of the country or state
            and update in in the address side 
            """
            
            try:
                serialized_data.save()
                return Response(serialized_data.data, status=201)
            except Exception as e:
                print(e)
                return Response({"details": "something went wrong"},status=403)
            
