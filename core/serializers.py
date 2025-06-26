from rest_framework import serializers
from . import models


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = '__all__'


#Serializer : Custom
#Model_Serializer : Automated From Model
class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    
    class Meta:
        model = models.Product
        fields = '__all__'
