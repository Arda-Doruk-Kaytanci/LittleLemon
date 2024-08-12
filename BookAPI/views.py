from django.contrib.auth.models import User
from rest_framework.authentication import TokenAuthentication
from .models import MenuItem, Category
from .serializers import MenuSerializer, CategorySerializer, UserSerializer, LoginSerializer, RegisterSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_protect
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework import generics, permissions
from rest_framework.exceptions import AuthenticationFailed
from django.shortcuts import redirect, render
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
@csrf_protect
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        serializer = RegisterSerializer(data={
            'username': username,
            'password': password
        })
        if serializer.is_valid():
            user = serializer.save()
            # Generate token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Return the tokens and redirect or render as needed
            response = render(request, 'BookAPI/register.html', {'message': 'Registration successful'})
            response.set_cookie('access', access_token, httponly=True)
            response.set_cookie('refresh', refresh_token, httponly=True)
            return response
        else:
            return render(request, 'BookAPI/register.html', {'errors': serializer.errors})

    return render(request, 'BookAPI/register.html')
@csrf_protect
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        serializer = LoginSerializer(data={
            'username': username,
            'password': password
        })
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Return the tokens and redirect or render as needed
            response = render(request, 'BookAPI/login.html', {'message': 'Login successful'})
            response.set_cookie('access', access_token, httponly=True)
            response.set_cookie('refresh', refresh_token, httponly=True)
            return response
        else:
            return render(request, 'BookAPI/login.html', {'errors': serializer.errors})

    return render(request, 'BookAPI/login.html')
@api_view(['GET', 'POST'])
def manage_staff_view(request):
    token = request.COOKIES.get('access')  # Get the access token from cookies

    if not token:
        return redirect('login')  # Redirect if no token is found

    try:
        # Verify the token
        access_token = AccessToken(token)
        user_id = access_token['user_id']
        user = User.objects.get(id=user_id)

        # Check if user is in the "Manager" group
        if not user.groups.filter(name='Manager').exists():
            return redirect('login')  # Redirect if user is not a manager

        if request.method == 'POST':
            username = request.POST.get('username')
            if username:
                try:
                    target_user = User.objects.get(username=username)
                    target_user.is_staff = True
                    target_user.save()
                    message = f'{username} has been assigned as staff.'
                except User.DoesNotExist:
                    message = 'User does not exist.'
                
                return render(request, 'BookAPI/manage_staff.html', {'message': message})
        
        return render(request, 'BookAPI/manage_staff.html')

    except AuthenticationFailed:
        return redirect('login')  # Redirect if token is invalid