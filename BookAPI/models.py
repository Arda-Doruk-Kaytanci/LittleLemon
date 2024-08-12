from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.title


class MenuItem(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    inventory = models.SmallIntegerField(default=1)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return self.name


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, default=1)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Cart {self.id} - User: {self.user.username}, Quantity: {self.quantity}"


class Order(models.Model):
    delivery_person = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, default=None, related_name="delivery")
    sent_by = models.ForeignKey(User, on_delete=models.PROTECT, default=1)
    items = models.ManyToManyField(CartItem) 

    def total_price(self):
        return sum(item.item.price * item.quantity for item in self.items.all())

    def __str__(self):
        if self.delivery_person:
            return f"Order {self.id} by {self.delivery_person.username}"
        return f"Order {self.id} - Not Assigned"
