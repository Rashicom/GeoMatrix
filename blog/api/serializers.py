from rest_framework import serializers
from .models import NormalUser, GovBodyUser, GovBodyAddress


# giv user signup
class GovSignupSeriaizers(serializers.ModelSerializer):
    class Meta:
        model = GovBodyUser
        fields = '__all__'



class GovBodyAddressSerializer(serializers.ModelSerializer):

    # excluding form is_valied() checking
    gov_body = serializers.CharField(required=False)
    class Meta:
        model = GovBodyAddress
        fields = '__all__'



# normal users
class NormalUserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = NormalUser
        fields = '__all__'

