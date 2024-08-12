from django.urls import path
from . import views

urlpatterns = [
    path('menu', views.MenuView.as_view()),
    path('menu/<int:pk>', views.MenuSingleItem.as_view()),
    path('category', views.CategoryView.as_view()), 
    path('user', views.UserView.as_view()),
    path('register', views.register_view, name='register'),
    path('login', views.login_view, name='login'),
    path('login/manage_staff', views.manage_staff_view, name='manage_staff')
]
