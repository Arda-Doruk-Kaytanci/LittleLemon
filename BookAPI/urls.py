from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

urlpatterns = [
    path("menu", views.MenuView.as_view()),
    path("menu/<int:pk>", views.MenuSingleItem.as_view()),
    path("cart", views.CartView.as_view()),
    path("cart/<int:pk>", views.CartSingleItem.as_view()),
    path("category", views.CategoryView.as_view()),
    path("user", views.UserView.as_view()),
    path("register", views.register_view, name="register"),
    path("login", views.user_login, name="login"),
    path("login/manage_staff", views.manage_staff_view, name="manage_staff"),
    path("login/home", views.home, name="home"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("logout/", views.user_logout, name="logout"),
    path("refresh-token/", views.refresh_token, name="refresh_token"),
    path("login/home/shop", views.shop, name="shop"),
    path("login/home/shop/cart", views.view_cart, name="cart"),
    path("login/home/show_order", views.view_orders, name="showorder"),
    path("login/home/assign_order", views.assign_order_view, name="assign_order"),
    path("login/home/orders", views.orders, name="view_order"),
    path(
        "mark-order-delivered/<int:order_id>/",
        views.mark_order_delivered,
        name="mark_order_delivered",
    ),
    path("generate_admin_token/", views.generate_admin_token, name="generate_admin_token"),
    path("refresh_admin_token/", views.refresh_admin_token, name="refresh_admin_token"),
]
