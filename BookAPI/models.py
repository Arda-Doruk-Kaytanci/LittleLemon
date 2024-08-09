from django.db import models

class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=255)
    def __str__(self)-> str:
        return self.title
    

class MenuItem(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    inventory = models.SmallIntegerField(default=1)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    def __str__(self)-> str:
        return self.name
    