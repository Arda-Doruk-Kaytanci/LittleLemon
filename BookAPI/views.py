from django.contrib.auth.models import User
from rest_framework.authentication import TokenAuthentication
from .models import MenuItem, Category
from .serializers import MenuSerializer, CategorySerializer, UserSerializer, serializers
from rest_framework import generics, permissions
from django.shortcuts import redirect
class MenuView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuSerializer
    search_fields = ['name']
class MenuSingleItem(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuSerializer
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return redirect('menu')
class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
class UserView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
