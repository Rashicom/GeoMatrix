from rest_framework import serializers
from .models import NormalUser, GovbodyUser, Gov_body_Address

# fornal users serializer
class NormalUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = NormalUser
        fields = '__all__'
    
        
# gov user serializer
class GovbodyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = GovbodyUser
        fields = '__all__'

class GovbodyUserAddressSerializer(serializers.ModelSerializer):
    # excluding forign key check from is_valid()
    gov_body = serializers.CharField(required=False)
    
    class Meta:
        model = Gov_body_Address
        fields = '__all__'