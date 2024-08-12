from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('menu', views.MenuView.as_view()),
    path('menu/<int:pk>', views.MenuSingleItem.as_view()),
    path('category', views.CategoryView.as_view()), 
    path('user', views.UserView.as_view()),
    path('register', views.register_view, name='register'),
    path('login', views.user_login, name='login'),
    path('login/manage_staff', views.manage_staff_view, name='manage_staff'),
    path('login/home', views.home, name="home"),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh')
]
