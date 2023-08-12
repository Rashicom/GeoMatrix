from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import authenticate
from .serializers import Custom_user_serializer, Login_serializer_user, Address_serializer, Wallet_transaction_serializer, Wallet_transactions_table_serializer
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
                return Response({"details": "something went wrong"},status=500)
            

# update profile picture
class update_user(APIView):
    
    permission_classes = [IsAuthenticated]
    serialzier_class = Custom_user_serializer
    def patch(self, request, format=None):
        """
        this function expecting any field of the user and update that specific field
        in the database and returning the updated user info
        """

        # prevent changing sensitive fields like social_rank, is_staff etc.
        for key in request.data.keys():
            if key in ["social_rank", "is_staff", "is_admin"]:
                return Response({"details": "you cant change this field"},status=400)
        
        # fetching and serializing it
        serializer = self.serialzier_class(request.user,data=request.data, partial=True)
        
        # validating data
        if serializer.is_valid(raise_exception=True):
            
            # saving updations
            try:
                serializer.save()
            except Exception as e:
                print(e)
                return Response({"details": "something went wrong"},status=500)
            # returning response
            return Response(serializer.data,status=201)



# new transaction
class new_transaction(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = Wallet_transaction_serializer

    def post(self, request, format=None):
        """
        fetching user and amound to be paid from the request and update
        """

        # fetching data and get wallet instence to update wattet transaction
        user = request.user
        wallet_instance = Wallet.objects.get(user_id = user)

        # serializing data
        serializer = self.serializer_class(data=request.data)
        
        # returning serializing error implicitly to the frond end.
        if serializer.is_valid(raise_exception=True):
            """
            fetch the data from the serailized data and update the data base
            then serializing the data and return back to user

            before updating the database we have to check the transaction type,
            and check the balance in the wallet to make a succussfull update,
            otherwise it returns a insufficiant balance warning
            """
            
            wallet_transaction_type = serializer.validated_data.get('wallet_transaction_type')
            wallet_transaction_amount = serializer.validated_data.get('wallet_transaction_amount')

            # buissiness logic for wallet balence cross match and upation
            # if the type is withdrowel
            if wallet_transaction_type == "WITHDRAWAL":
                """
                only withdrow the money from wallet if there are sufficient balance in the account
                otherwise it returns insufficiant balance
                """
                if wallet_transaction_amount > wallet_instance.balance:
                    return Response({"details":"insufficient balance"},status=403)
                else:
                    wallet_instance.balance = wallet_instance.balance - wallet_transaction_amount
            
            # if the type is deposit
            elif wallet_transaction_type == "DEPOSIT":
                wallet_instance.balance += wallet_transaction_amount
            
            # save the wallet instence
            wallet_instance.save()

            try:
                # creatiing wallet transaction and return response
                new_transaction = serializer.save(wallet = wallet_instance)

            except Exception as e:
                print(e)
                return Response({"details":"something went wrong"},status=403)

            # serializing the new transaction and return back to user
            # here a new serializer is used to return all data, class serializer only return type and amount
            transaction_serializer = Wallet_transactions_table_serializer(new_transaction)
            return Response(transaction_serializer.data,status=201)
