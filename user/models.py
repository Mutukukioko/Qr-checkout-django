from django.db import models
from django.contrib.auth.models import User
import uuid

# Create your models here.

class Product(models.Model):
    CATEGORY = (
        ('Kitchen','Home appliance'),
        ('Cloths','Shoes'),
        ('electricals','non electric'),
    )
    name = models.CharField(max_length=50)
    price = models.IntegerField()
    shop_id = models.CharField(max_length=254)
    category = models.CharField(max_length = 254, null=True, choices= CATEGORY)
    brand = models.CharField(max_length = 254)
    quantity = models.CharField(max_length = 254)
    picture = models.ImageField(upload_to="img", default="")

    def __str__(self):
        return self.name

class Cart(models.Model):
    id =models.UUIDField(default = uuid.uuid4, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    completed = models.BooleanField(default = False)
    
    
    def __str__(self):
        return str(self.id)        


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete = models.CASCADE, related_name = 'cartitems')
    cart = models.ForeignKey(Cart, on_delete = models.CASCADE, related_name = 'cartitems')
    quantity = models.IntegerField(default = 0)

    def __str__(self):
        return self.product.name

class Shop(models.Model):
    shop_name = models.CharField(max_length = 200)
    location = models.CharField(max_length = 200)
    logo = models.ImageField(upload_to="img", default="")
    email = models.EmailField(max_length = 254)
    password = models.CharField(max_length = 254)

    def __str__(self):
        return self.shop_name
    
class Item(models.Model):
    name = models.CharField(max_length=100)
    barcode = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='item_images', null=True, blank=True)

    def __str__(self):
        return self.name