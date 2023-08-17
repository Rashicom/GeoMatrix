from .models import CustomUser, Address, Wallet, Wallet_transaction
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
