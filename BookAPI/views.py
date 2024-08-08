from django.shortcuts import render

# Create your views here.

from .models import MenuItem, Category
from .serializers import MenuSerializer, CategorySerializer
from rest_framework import generics

class MenuView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuSerializer

class MenuSingleItem(generics.RetrieveUpdateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuSerializer
class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer