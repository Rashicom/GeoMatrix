from rest_framework import serializers
from .models import about_section, service_section,product_section

class main_section_serializer(serializers.Serializer):
    title = serializers.CharField()
    description = serializers.CharField()
    image = serializers.ImageField()


class main_section_serializer_get(serializers.Serializer):
    title = serializers.CharField()
    description = serializers.ListField(child = serializers.CharField())
    image = serializers.ListField(child = serializers.ImageField())
    


class about_section_serializer(serializers.ModelSerializer):
    class Meta:
        model = about_section
        fields = '__all__'


class product_section_serializer(serializers.ModelSerializer):
    class Meta:
        model = product_section
        fields = '__all__'


class service_section_serializer(serializers.ModelSerializer):
    class Meta:
        model = service_section
        fields = '__all__'
