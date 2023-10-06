from rest_framework import serializers
from .models import NormalUser, GovbodyUser, Gov_body_Address, Land, LandGeography, LandOwnershipRegistry, LandTypeTaxList, TaxInvoice



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
        depth = 1



class LandOwnershipRegistrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LandOwnershipRegistry
        fields = '__all__'



class ChangeOwnershipRegistrySerializer(serializers.Serializer):
    owner_email = serializers.EmailField()
    new_owner_email = serializers.EmailField()
    land_number = serializers.IntegerField()



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
    


class LandDataResponseSerializer(serializers.Serializer):
    land = serializers.IntegerField()
    land_type = serializers.CharField()
    location_coordinate = serializers.ListField()
    boundary_polygon = serializers.ListField()
    area = serializers.FloatField()


class LandGeographyfilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandGeography
        fields = '__all__'


class DateFilteredLandSerializer(serializers.ModelSerializer):
    land_geography = LandGeographyfilterSerializer()
    class Meta:
        model = Land
        fields = [
                    'land_number',
                    'user',
                    'locality',
                    'district',
                    'state',
                    'zip_code',
                    'land_geography'
                ]
        



class LandSplitSerializer(serializers.Serializer):
    land_record_file = serializers.FileField()
    parent_land_number = serializers.IntegerField()
    parent_user_email = serializers.EmailField()
    

class LandRegistrationMultipleUsers(LandRegistraionSerailizer):
    # suing LandRegistraionSerailizer fields plus adissional fields
    
    # insted of email we have to specify owner_email
    email = None
    owner_email = serializers.EmailField()



# for crud on land tax table
class LandTypeTaxListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LandTypeTaxList
        fields = '__all__'



class TaxInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxInvoice
        fields = '__all__'
        

class LandInAddressSerializer(serializers.Serializer):
    state = serializers.CharField(required=False)
    district = serializers.CharField(required=False)
    locality = serializers.CharField(required=False)
    zip_code = serializers.CharField(required=False)
    active_land_only = serializers.BooleanField(required=False)
