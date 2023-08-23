from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import authenticate
from .serializers import (
    Custom_user_serializer,
    Login_serializer_user,
    Address_serializer,
    Wallet_transaction_serializer,
    Wallet_transactions_table_serializer,

    governmental_body_user_serializer,
    gov_body_Address_serializer,
    gov_body_wallet_serializer,
    GovuserLoginSerializer,
    GovwalletTransactionSerializer,

)
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Wallet, Address, Wallet_transaction, Gov_body_wallet, Gov_body_user, Gov_body_wallet_transaction
from datetime import date
from django.db.models import Q
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import transaction
from .helper import UniqueGovUser
from .Customauthentication import authenticate_govuser
from .Customauthentication import GovuserJwtAuthentication
# Create your views here.


# user creation
class signup(APIView):
    permission_classes = [AllowAny]
    serializer_class = Custom_user_serializer

    def post(self, request, format=None):
        """
        creating user, recieving request.data and serialzing it, then
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
            hashed_password = make_password(serializer.validated_data["password"])
            user = serializer.save(password=hashed_password)

            # excluding password from the response and send response
            response_data = serializer.data

            # updating wallet table
            new_wallet = Wallet(user=user)
            new_wallet.save()

            # removing password from response and send response
            response_data.pop("password")
            print("user created")
            return Response(response_data, status=201)



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
            email = seriazed_data.validated_data["email"]
            password = seriazed_data.validated_data["password"]

            # authenticate func returns user instence if authenticated
            user = authenticate(email=email, password=password)

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
                        "email": email,
                        "password": password,
                        "access": str(access),
                        "refresh": str(refresh),
                    },
                    status=201,
                )

            # if user none, wrong email or passord
            else:
                return Response({"details": "wrong email or password"}, status=401)


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
                serializer.save(user=user)
            except Exception as e:
                print(e)
                return Response({"details": "somthing went wrong"}, status=400)
            return Response(serializer.data, status=201)



# edit address
# edit address
class edit_address(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = Address_serializer

    def patch(self, request, format=None):
        """
        updating user address details
        """

        address_instence = Address.objects.get(user=request.user)
        # serializing data
        serialized_data = self.serializer_class(
            address_instence, data=request.data, partial=True
        )

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
                return Response({"details": "something went wrong"}, status=500)



# get address
class get_address(APIView):
    permission_classes = [IsAuthenticated]
    serialzier_class = Address_serializer

    def get(self, request, format=None):
        address = Address.objects.get(user=request.user)
        serializer = self.serialzier_class(address)
        print(serializer.data)
        return Response(serializer.data, status=200)


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
                return Response({"details": "you cant change this field"}, status=400)

        # fetching and serializing it
        serializer = self.serialzier_class(
            request.user, data=request.data, partial=True
        )

        # validating data
        if serializer.is_valid(raise_exception=True):

            # saving updations
            try:
                serializer.save()
            except Exception as e:
                print(e)
                return Response({"details": "something went wrong"}, status=500)
            # returning response
            return Response(serializer.data, status=201)


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
        wallet_instance = Wallet.objects.get(user_id=user)

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

            wallet_transaction_type = serializer.validated_data.get(
                "wallet_transaction_type"
            )
            wallet_transaction_amount = serializer.validated_data.get(
                "wallet_transaction_amount"
            )

            # buissiness logic for wallet balence cross match and upation
            # if the type is withdrowel
            if wallet_transaction_type == "WITHDRAWAL":
                """
                only withdrow the money from wallet if there are sufficient balance in the account
                otherwise it returns insufficiant balance
                """
                if wallet_transaction_amount > wallet_instance.balance:
                    return Response({"details": "insufficient balance"}, status=403)
                else:
                    wallet_instance.balance = (
                        wallet_instance.balance - wallet_transaction_amount
                    )

            # if the type is deposit
            elif wallet_transaction_type == "DEPOSIT":
                wallet_instance.balance += wallet_transaction_amount

            # save the wallet instence
            wallet_instance.save()

            try:
                # creatiing wallet transaction and return response
                new_transaction = serializer.save(wallet=wallet_instance)

            except Exception as e:
                print(e)
                return Response({"details": "something went wrong"}, status=403)

            # serializing the new transaction and return back to user
            # here a new serializer is used to return all data, class serializer only return type and amount
            transaction_serializer = Wallet_transactions_table_serializer(
                new_transaction
            )
            return Response(transaction_serializer.data, status=201)


# wallet balance
class get_wallet_balance(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        """
        fetching user wallet balance
        """
        user = request.user
        wallet_instence = Wallet.objects.get(user=user)
        return Response({"balance": wallet_instence.balance}, status=200)


# get vallet transaction by transactin id
class get_wallet_transaction(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = Wallet_transactions_table_serializer

    def get(self, request, format=None):
        """
        this function searching for a perticular transaction by transaction id
        which given by the user and fetching the transactin details and send back
        """

        # fetching data from params
        wallet_transaction_id = request.query_params.get("wallet_transaction_id")

        # fetching transaction details by given transaction id
        try:
            transaction = Wallet_transaction.objects.get(
                wallet_transaction_id=wallet_transaction_id
            )
        except Exception as e:
            print(e)
            return Response({"details": "transaction not found"}, status=404)

        # serializing data if the tranacion found and return
        serializer = self.serializer_class(transaction)
        return Response(serializer.data, status=200)


# transaction history
class transaction_history(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = Wallet_transactions_table_serializer

    def get(self, request, format=None):
        """
        filtering the users transaction history by date
        date_from is set to today date if date_from is not provided
        and to date set to None
        """

        # fetching data from params
        date_from = request.query_params.get("date_from", None)
        date_to = request.query_params.get("date_to", date.today())

        # wallet instance to filter
        user = request.user
        wallet_instance = Wallet.objects.get(user=user)

        # filtering logic
        if date_from == None:
            transactions = Q(wallet_id=wallet_instance) & Q(
                wallet_transaction_date__lte=date_to
            )

        else:
            transactions = (
                Q(wallet_id=wallet_instance)
                & Q(wallet_transaction_date__lte=date_to)
                & Q(wallet_transaction_date__gte=date_from)
            )
        
        # filtering wallet transaction history and serializing data
        transactions = Wallet_transaction.objects.filter(transactions)
        serialized_data = self.serializer_class(transactions, many=True)

        return Response(serialized_data.data, status=200)




"//////////////////////////  Gov_body_user  ////////////////////////////////"

class gov_body_signup(APIView):
    permission_classes = [AllowAny]
    serializer_class = governmental_body_user_serializer

    def post(self, request, format=None):
        """
        creating a user with role
        creating a address for the user, and update address
        create a zero balance account for the user then return info
        """

        # serializing data for gov user table
        gov_body_serializer = self.serializer_class(data=request.data)
        gov_body_serializer.is_valid(raise_exception=True)

        # serializing data fro gov_users address
        gov_body_address_serializer = gov_body_Address_serializer(data=request.data)
        gov_body_address_serializer.is_valid(raise_exception=True)
        
        # checking the user is unique for a perticular place
        # cannot create two gov body's for a same location
        # fetchind role and address data for checking
        role = gov_body_serializer.validated_data.get("role")
        state = gov_body_address_serializer.validated_data.get("state")
        district = gov_body_address_serializer.validated_data.get("district")
        locality = gov_body_address_serializer.validated_data.get("locality")
        
        # checkign existing gov_user in the smae role and same place
        try:
            gov_user = UniqueGovUser(role=role, state=state, district=district, locality=locality)
            unique = gov_user.is_unique()

        except Exception as e:
            print(e)
            return Response({"details":"somthing went wrong"},status=500)
        

        # if the user already exists return conflict status
        if not unique:
            return Response({"details":"User already exist for this teritory"},status=409)
        
        # hashing password to create user
        hashed_password = make_password(gov_body_serializer.validated_data.get("password"))
        
        try:

            # if any excepton found table updations are roll backed
            with transaction.atomic():

                # if user is unique procede to create new gov user
                new_gov_user = gov_body_serializer.save(password=hashed_password, is_active=True)
                gov_user_address = gov_body_address_serializer.save(gov_body=new_gov_user)
                
                # create a new wallet for the new gov user
                new_wallet = Gov_body_wallet.objects.create(Gov_body=new_gov_user)
                
                new_wallet_data = gov_body_wallet_serializer(new_wallet)
                

        except Exception as e:
            print(e)
            return Response({"details":"somthing went wrong"},status=500)

        # returning all the created data. user, address and wallet details
        return Response(
            {"user":gov_body_serializer.data,
            "address":gov_body_address_serializer.data,
            "wallet":new_wallet_data.data
            },
            status=201
        )
      
        
# login
class GovBodylogin(APIView):
  
    serializer_class = GovuserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        """
        validating the user credencials and generating access and refresh
        jwt tocken if the user is validated otherwise return error message
        """
        print("login request hit")
        # serializing data
        seriazed_data = self.serializer_class(data=request.data)

        # validating credencians, if credencials invalied error message
        # automatically send to frond end
        if seriazed_data.is_valid(raise_exception=True):
  
            # fetching credencials for validation
            email = seriazed_data.validated_data["email"]
            password = seriazed_data.validated_data["password"]

            # authenticate func returns user instence if authenticated
            # this is custom authenticated function writen in customauthentication.py
            user = authenticate_govuser(email=email,password=password)

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
                        "email": email,
                        "access": str(access),
                        "refresh": str(refresh),
                    },
                    status=201,
                )

            # if user none, wrong email or passord
            else:
                return Response({"details": "wrong email or password"}, status=401)
        
            

# get wallet balance
class GetGovwalletbalance(APIView):
    authentication_classes = [GovuserJwtAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        wallet = Gov_body_wallet.objects.get(Gov_body=request.user)

        
        return Response(
            {
                "id": wallet.wallet_id,
                "balance": wallet.balance
            },
            status=200
        )


# new transaction
class GovnewTransaction(APIView):

    authentication_classes = [GovuserJwtAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = GovwalletTransactionSerializer

    # wallet model used int this class
    wallet_model = Gov_body_wallet

    def post(self, request, format=None):
        """
        fetching user and amound to be paid from the request and update
        """

        # fetching data and get wallet instence to update wattet transaction
        user = request.user
        wallet_instance = self.wallet_model.objects.get(Gov_body=user)

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

            wallet_transaction_type = serializer.validated_data.get(
                "wallet_transaction_type"
            )
            wallet_transaction_amount = serializer.validated_data.get(
                "wallet_transaction_amount"
            )

            # buissiness logic for wallet balence cross match and upation
            # if the type is withdrowel
            if wallet_transaction_type == "WITHDRAWAL":
                """
                only withdrow the money from wallet if there are sufficient balance in the account
                otherwise it returns insufficiant balance
                """
                if wallet_transaction_amount > wallet_instance.balance:
                    return Response({"details": "insufficient balance"}, status=403)
                else:
                    wallet_instance.balance = (
                        wallet_instance.balance - wallet_transaction_amount
                    )

            # if the type is deposit
            elif wallet_transaction_type == "DEPOSIT":
                wallet_instance.balance += wallet_transaction_amount

            # save the wallet instence
            wallet_instance.save()

            try:
                # creatiing wallet transaction and return response
                new_transaction = serializer.save(wallet=wallet_instance)

            except Exception as e:
                print(e)
                return Response({"details": "something went wrong"}, status=403)

            # serializing the new transaction and return back to user
            # here a new serializer is used to return all data, class serializer only return type and amount
            return Response(serializer.data, status=201)



# transaction history
class GovTransactionHistory(APIView):

    authentication_classes = [GovuserJwtAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = GovwalletTransactionSerializer

    # wallet model used int this class
    wallet_model = Gov_body_wallet

    def get(self, request, format=None):
        """
        filtering the users transaction history by date
        date_from is set to today date if date_from is not provided
        and to date set to None
        """

        # fetching data from params
        date_from = request.query_params.get("date_from", None)
        date_to = request.query_params.get("date_to", date.today())

        # wallet instance to filter
        user = request.user
        wallet_instance = self.wallet_model.objects.get(Gov_body=user)

        # filtering logic
        if date_from == None:
            transactions = Q(wallet_id=wallet_instance) & Q(
                wallet_transaction_date__lte=date_to
            )

        else:
            transactions = (
                Q(wallet_id=wallet_instance)
                & Q(wallet_transaction_date__lte=date_to)
                & Q(wallet_transaction_date__gte=date_from)
            )
        
        # filtering wallet transaction history and serializing data
        transactions = Gov_body_wallet_transaction.objects.filter(transactions)
        serialized_data = self.serializer_class(transactions, many=True)

        return Response(serialized_data.data, status=200)