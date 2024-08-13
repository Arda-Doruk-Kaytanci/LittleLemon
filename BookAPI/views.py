from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import logout as auth_logout
from rest_framework_simplejwt.exceptions import TokenError
from .forms import AssignOrderForm
from .models import MenuItem, Category, CartItem, Order, ItemOfTheDay
from .serializers import (
    MenuSerializer,
    CategorySerializer,
    UserSerializer,
    CartSerializer,
    RegisterSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, login
from rest_framework import generics, permissions
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
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        serializer = RegisterSerializer(
            data={"username": username, "password": password}
        )
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            response = redirect("login")
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
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

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
def manage_staff_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        role = request.POST.get("role")

        try:
            user = User.objects.get(username=username)
            if role == "manager":
                user.groups.add(Group.objects.get(name="manager"))
            elif role == "staff":
                user.groups.add(Group.objects.get(name="staff"))
            elif role == "delivery":
                user.groups.add(Group.objects.get(name="delivery"))
        except User.DoesNotExist:
            pass

        return redirect("manage_staff")

    users = User.objects.all()
    is_superuser = request.user.is_superuser
    is_manager = request.user.groups.filter(name="manager").exists()
    return render(
        request,
        "BookAPI/manage_staff.html",
        {"users": users, "is_superuser": is_superuser, "is_manager": is_manager},
    )


@login_required
def home(request):
    user = request.user
    is_manager = user.groups.filter(name="manager").exists()

    item_of_the_day = ItemOfTheDay.objects.first()

    if request.method == "POST":
        if "update_item_of_the_day" in request.POST:
            item_id = request.POST.get("item_id")
            if item_id:
                item = MenuItem.objects.get(id=item_id)
                ItemOfTheDay.objects.update_or_create(defaults={"item": item})

    return render(
        request,
        "BookAPI/home.html",
        {
            "username": user.username,
            "is_manager": is_manager,
            "item_of_the_day": item_of_the_day.item if item_of_the_day else None,
            "menu_items": MenuItem.objects.all(),
        },
    )


@login_required
@csrf_protect
def refresh_token(request):
    if request.method == "POST":
        refresh_token = request.COOKIES.get("refresh")
        if not refresh_token:
            return redirect("login")

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

            if "is_admin" in refresh.access_token and refresh.access_token["is_admin"]:
                pass

            return response
        except TokenError:
            return redirect("login")

    return redirect("home")


@login_required
@csrf_protect
def user_logout(request):
    auth_logout(request)
    response = redirect("login")
    response.delete_cookie("access")
    response.delete_cookie("refresh")
    return response


@login_required
def shop(request):
    items = MenuItem.objects.all()
    categories = Category.objects.all()

    search_query = request.GET.get("search", "")
    sort_by = request.GET.get("sort_by", "")
    order = request.GET.get("order", "asc")
    category_id = request.GET.get("category", "")

    if search_query:
        items = items.filter(name__icontains=search_query)

    if category_id:
        items = items.filter(category_id=category_id)

    sort_prefix = "-" if order == "desc" else ""
    if sort_by == "category":
        items = items.order_by(f"{sort_prefix}category__title")
    elif sort_by == "price":
        items = items.order_by(f"{sort_prefix}price")

    total_price = sum(item.price for item in items)

    if request.method == "POST":
        item_id = request.POST.get("item_id")
        quantity = request.POST.get("quantity", 1)
        item = MenuItem.objects.get(id=item_id)
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user, item=item, defaults={"quantity": quantity}
        )
        if not created:
            cart_item.quantity += int(quantity)
            cart_item.save()

        return redirect("shop")

    return render(
        request,
        "BookAPI/shop.html",
        {
            "menu": items,
            "total": total_price,
            "categories": categories,
            "selected_category": category_id,
        },
    )


@login_required
def view_cart(request):
    if request.method == "POST":
        action = request.POST.get("action")
        item_id = request.POST.get("item_id")

        if action == "remove" and item_id:
            try:
                cart_item = CartItem.objects.get(id=item_id, user=request.user)
                cart_item.delete()
            except CartItem.DoesNotExist:
                pass

        elif action == "decrease" and item_id:
            try:
                cart_item = CartItem.objects.get(id=item_id, user=request.user)
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                    cart_item.save()
                else:
                    cart_item.delete()
            except CartItem.DoesNotExist:
                pass

        elif action == "finish_order":
            order = Order.objects.create(sent_by=request.user)
            cart_items = CartItem.objects.filter(user=request.user)
            order.items.set(cart_items)
            order.save()
            return redirect("cart")

        return redirect("cart")

    # Sorting and Pagination
    sort_by = request.GET.get("sort_by", "name")  # Default sorting by 'name'
    sort_order = request.GET.get("order", "asc")  # Default to ascending order

    # Define sorting fields
    sort_fields = {
        "name": "item__name",
        "price": "item__price",
        "quantity": "quantity",
    }

    # Apply sorting and pagination
    sort_field = sort_fields.get(sort_by, "item__name")
    ordering = f"{'-' if sort_order == 'desc' else ''}{sort_field}"
    cart_items = CartItem.objects.filter(user=request.user).order_by(ordering)

    # Pagination
    paginator = Paginator(cart_items, 10)  # Show 10 items per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    total_price = sum(item.item.price * item.quantity for item in page_obj)

    return render(
        request,
        "BookAPI/cart.html",
        {
            "cart_items": page_obj,
            "total_price": total_price,
            "sort_by": sort_by,
            "order": sort_order,
        },
    )


@login_required
def view_orders(request):
    if request.user.groups.filter(name="Deliver").exists():
        if request.method == "POST":
            order_id = request.POST.get("order_id")
            try:
                order = Order.objects.get(id=order_id, delivery_person=request.user)
                order.delivered = True
                order.save()
            except Order.DoesNotExist:
                pass
            return redirect("view_orders")

        orders = Order.objects.filter(delivery_person=request.user)
        return render(request, "BookAPI/vieworder.html", {"orders": orders})
    else:
        return redirect("home")


def is_manager(user):
    return user.groups.filter(name="Manager").exists()


@login_required
@user_passes_test(is_manager, login_url="home")
def assign_order_view(request):
    if request.method == "POST":
        form = AssignOrderForm(request.POST)
        if form.is_valid():
            order_id = form.cleaned_data["order_id"]
            username = form.cleaned_data["username"]

            try:
                order = Order.objects.get(id=order_id)
                delivery_person = User.objects.get(username=username)
                order.delivery_person = delivery_person
                order.save()

                return redirect("assign_order")  #
            except Order.DoesNotExist:
                form.add_error("order_id", "The order does not exist.")
            except User.DoesNotExist:
                form.add_error("username", "The delivery person does not exist.")

    else:
        form = AssignOrderForm()

    return render(request, "BookAPI/assign_order.html", {"form": form})


@login_required
def orders(request):
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        try:
            order = Order.objects.get(id=order_id, sent_by=request.user)
            order.delivered = True
            order.save()
        except Order.DoesNotExist:
            pass

        return redirect("view_order")

    sort_by = request.GET.get("sort_by", "id")
    order = request.GET.get("order", "asc")

    sort_fields = {
        "id": "id",
        "price": "price",
        "delivered": "delivered",
    }

    sort_field = sort_fields.get(sort_by, "id")
    sort_order = "" if order == "asc" else "-"

    orders = Order.objects.filter(sent_by=request.user).order_by(
        f"{sort_order}{sort_field}"
    )

    paginator = Paginator(orders, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "BookAPI/orders.html",
        {"orders": page_obj, "sort_by": sort_by, "order": order},
    )


@login_required
def mark_order_delivered(request, order_id):
    if request.user.groups.filter(name="Deliver").exists():
        try:
            order = Order.objects.get(id=order_id, delivery_person=request.user)
            order.delivered = True
            order.save()
        except Order.DoesNotExist:
            pass
    return redirect("view_order")


@login_required
def generate_admin_token(request):
    if request.user.is_superuser:
        refresh = RefreshToken.for_user(request.user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        response = redirect("home")
        response.set_cookie(
            "admin_access",
            access_token,
            max_age=3600,
            httponly=True,
            secure=True,
            samesite="Lax",
        )
        response.set_cookie(
            "admin_refresh",
            refresh_token,
            max_age=86400 * 7,
            httponly=True,
            secure=True,
            samesite="Lax",
        )
        return response
    else:
        return redirect("home")


@login_required
def refresh_admin_token(request):
    if request.user.is_superuser:
        refresh_token = request.COOKIES.get("admin_refresh")
        if not refresh_token:
            return redirect("login")

        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)
            new_refresh_token = str(refresh)
            response = redirect("home")
            response.set_cookie(
                "admin_access",
                new_access_token,
                max_age=3600,
                httponly=True,
                secure=True,
                samesite="Lax",
            )
            response.set_cookie(
                "admin_refresh",
                new_refresh_token,
                max_age=86400 * 7,
                httponly=True,
                secure=True,
                samesite="Lax",
            )
            return response
        except TokenError:
            return redirect("login")
    else:
        return redirect("home")
