from .models import CustomUser, Address, Wallet_transaction, Gov_body_user, Gov_body_Address,Gov_body_wallet
from rest_framework import serializers


class Custom_user_serializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "adhar_id",
            "contact_number",
            "social_rank",
            "password",
        ]


class Login_serializer_user(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class Address_serializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "address_id",
            "address",
            "locality",
            "district",
            "state",
            "zipcode",
            "country",
        ]


class Wallet_transaction_serializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet_transaction
        fields = ["wallet_transaction_type", "wallet_transaction_amount"]


class Wallet_transactions_table_serializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet_transaction
        fields = "__all__"





"//////////////////////////  Gov_body_user serializers  ////////////////////////////////"

# for creating admin user
class governmental_body_user_serializer(serializers.ModelSerializer):   
    class Meta:
        model = Gov_body_user
        fields = '__all__'

# for creating and updating address
class gov_body_Address_serializer(serializers.ModelSerializer):
    class Meta:
        model = Gov_body_Address
        fields = ['locality','district','state','country']


class gov_body_wallet_serializer(serializers.ModelSerializer):
    class Meta:
        model = Gov_body_wallet
        fields = '__all__'




