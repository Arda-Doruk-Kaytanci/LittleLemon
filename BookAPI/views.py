from django.contrib.auth.models import User
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import logout as auth_logout 
from rest_framework_simplejwt.exceptions import TokenError
from .models import MenuItem, Category
from .serializers import (
    MenuSerializer,
    CategorySerializer,
    UserSerializer,
    LoginSerializer,
    RegisterSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, login
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework import generics, permissions
from rest_framework.exceptions import AuthenticationFailed
from django.shortcuts import redirect, render


class MenuView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuSerializer
    search_fields = ["name"]


class MenuSingleItem(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return redirect("menu")


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
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        serializer = RegisterSerializer(
            data={"username": username, "password": password}
        )
        if serializer.is_valid():
            user = serializer.save()
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Create response object
            response = redirect("login/home")
            response.set_cookie(
                "access",
                access_token,
                max_age=3600,
                httponly=True,
                secure=True,
                samesite="Lax",
            )
            response.set_cookie(
                "refresh",
                refresh_token,
                max_age=86400 * 7,
                httponly=True,
                secure=True,
                samesite="Lax",
            )

            return response
        else:
            return render(
                request, "BookAPI/register.html", {"errors": serializer.errors}
            )

    return render(request, "BookAPI/register.html")


@csrf_protect
def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Generate new JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Create response object
            response = redirect("home")
            response.set_cookie(
                "access",
                access_token,
                max_age=3600,
                httponly=True,
                secure=True,
                samesite="Lax",
            )
            response.set_cookie(
                "refresh",
                refresh_token,
                max_age=86400 * 7,
                httponly=True,
                secure=True,
                samesite="Lax",
            )

            return response
        else:
            return render(
                request, "BookAPI/login.html", {"error": "Invalid credentials"}
            )

    return render(request, "BookAPI/login.html")


@api_view(["GET", "POST"])
def manage_staff_view(request):
    token = request.COOKIES.get("access")  # Get the access token from cookies

    if not token:
        return redirect("login")  # Redirect if no token is found

    try:
        # Verify the token
        access_token = AccessToken(token)
        user_id = access_token["user_id"]
        user = User.objects.get(id=user_id)

        # Check if user is in the "Manager" group
        if not user.groups.filter(name="Manager").exists():
            return redirect("login")  # Redirect if user is not a manager

        if request.method == "POST":
            username = request.POST.get("username")
            if username:
                try:
                    target_user = User.objects.get(username=username)
                    target_user.is_staff = True
                    target_user.save()
                    message = f"{username} has been assigned as staff."
                except User.DoesNotExist:
                    message = "User does not exist."

                return render(
                    request,
                    "BookAPI/manage_staff.html",
                    {"message": message, "users": User.objects.all()},
                )

        # Fetch all users to be shown in the select list
        users = User.objects.exclude(
            username=user.username
        )  # Exclude current user if needed
        return render(request, "BookAPI/manage_staff.html", {"users": users})

    except AuthenticationFailed:
        return redirect("login")


@login_required
def home(request):
    user = request.user
    return render(request, "BookAPI/home.html", {"username": user.username})


@csrf_protect
def refresh_token(request):
    if request.method == "POST":
        refresh_token = request.COOKIES.get("refresh")
        if not refresh_token:
            return redirect("login")  # Redirect if no refresh token is found

        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)
            new_refresh_token = str(refresh)
            response = redirect("home")
            response.set_cookie(
                "access",
                new_access_token,
                max_age=3600,
                httponly=True,
                secure=True,
                samesite="Lax",
            )
            response.set_cookie(
                "refresh",
                new_refresh_token,
                max_age=86400 * 7,
                httponly=True,
                secure=True,
                samesite="Lax",
            )
            return response
        except TokenError:
            return redirect("login")  # Redirect if token is invalid

    return redirect("home")


@csrf_protect
def user_logout(request):
    auth_logout(request)  # Clear the session
    response = redirect("login")
    response.delete_cookie("access")
    response.delete_cookie("refresh")
    return response
