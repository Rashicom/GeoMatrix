from rest_framework import serializers
from .models import NormalUser, GovbodyUser, Gov_body_Address, Land, LandGeography, LandOwnershipRegistry

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


class LandSerializer(serializers.ModelSerializer):

    # excluding forign key from validaion
    user = serializers.CharField(required=False)

    class Meta:
        model = Land
        fields = '__all__'


class LandOwnershipRegistrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LandOwnershipRegistry
        fields = '__all__'

class ChangeOwnershipRegistrySerializer(serializers.Serializer):
    owner = serializers.CharField(required=True)
    new_owner = serializers.CharField(required=True)
    

class LandGeographySerializer(serializers.ModelSerializer):
    class Meta:
        model = LandGeography
        fields = '__all__'
        depth = 1


# land registration serializer
class LandRegistraionSerailizer(serializers.Serializer):
    # for identify for which user land belongs to
    email = serializers.EmailField(required=True)

    # updating land table
    locality = serializers.CharField(required=True)
    district = serializers.CharField(required=True)
    state = serializers.CharField(required=True)
    zip_code = serializers.CharField(required=True)

    # updating landgeography
    # other fields need to becalculated just befor saving
    land_type = serializers.ChoiceField(choices=LandGeography.Choices.choices)
    boundary_polygon = serializers.ListField()
    

