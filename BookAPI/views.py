from django.contrib.auth.models import User
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import logout as auth_logout
from rest_framework_simplejwt.exceptions import TokenError
from .models import MenuItem, Category, CartItem
from .serializers import (
    MenuSerializer,
    CategorySerializer,
    UserSerializer,
    LoginSerializer,
    CartSerializer,
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


class CartView(generics.ListAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartSerializer


class CartSingleItem(generics.RetrieveAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartSerializer


class UserView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


@csrf_protect
def register_view(request):
    # Check if the user is already authenticated
    if request.user.is_authenticated:
        return redirect("login")  # Adjust this to your URL name

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
            response = redirect("login")  # Adjust this to your URL name
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


@login_required
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
        return redirect("home")  # Redirect to home page on token error
    except Exception as e:
        # Handle unexpected errors
        print(f"Unexpected error: {e}")
        return redirect("home")


@login_required
def home(request):
    user = request.user
    is_manager = user.groups.filter(
        name="manager"
    ).exists()  # Check if user is in 'manager' group
    return render(
        request,
        "BookAPI/home.html",
        {"username": user.username, "is_manager": is_manager},
    )


@login_required
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


@login_required
@csrf_protect
def user_logout(request):
    auth_logout(request)  # Clear the session
    response = redirect("login")
    response.delete_cookie("access")
    response.delete_cookie("refresh")
    return response


@login_required
def shop(request):
    items = MenuItem.objects.all()
    total_price = sum(item.price for item in items)

    if request.method == "POST":
        item_id = request.POST.get("item_id")
        quantity = request.POST.get("quantity", 1)
        item = MenuItem.objects.get(id=item_id)

        # Create or update the CartItem for this user and item
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user, item=item, defaults={"quantity": quantity}
        )
        if not created:
            cart_item.quantity += int(quantity)
            cart_item.save()

        return redirect("shop")  # Redirect to the shop page after adding to the cart

    return render(request, "BookAPI/shop.html", {"menu": items, "total": total_price})


@login_required
def view_cart(request):
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        action = request.POST.get("action")

        if item_id and action:
            try:
                cart_item = CartItem.objects.get(id=item_id, user=request.user)

                if action == "remove":
                    cart_item.delete()  # Remove the item if requested
                elif action == "decrease" and cart_item.quantity > 1:
                    cart_item.quantity -= 1  # Decrease quantity
                    cart_item.save()
                # Optionally handle an "increase" action if needed

            except CartItem.DoesNotExist:
                pass  # Handle the case where the item does not exist or does not belong to the user

        return redirect("cart")  # Redirect to the cart page after modification

    # Retrieve all cart items for the logged-in user
    cart_items = CartItem.objects.filter(user=request.user)

    # Calculate the total price
    total_price = sum(item.item.price * item.quantity for item in cart_items)

    return render(
        request,
        "BookAPI/cart.html",
        {"cart_items": cart_items, "total_price": total_price},
    )
