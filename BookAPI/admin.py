from django.contrib import admin
from .models import MenuItem, Category, CartItem

admin.site.register(CartItem)
admin.site.register(MenuItem)
admin.site.register(Category)