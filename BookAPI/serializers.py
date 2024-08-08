from rest_framework import serializers
from .models import MenuItem, Category
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['title', 'id']
class MenuSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only = True)
    category = CategorySerializer(read_only = True)
    class Meta:
        model = MenuItem
        fields = ['name', 'price', 'category', 'id', 'category_id', 'inventory',]

