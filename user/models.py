from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone




class Shop(models.Model):
    shop_name = models.CharField(max_length = 200)
    location = models.CharField(max_length = 200)
    logo = models.ImageField(upload_to="img", default="")
    qrval = models.CharField(max_length=254, unique=True, default="")
    email = models.EmailField(max_length = 254)
    password = models.CharField(max_length = 254)

    def __str__(self):
        return self.shop_name

class Product(models.Model):
    CATEGORY = (
        ('Kitchen','Home appliance'),
        ('Cloths','Shoes'),
        ('electricals','non electric'),
    )
    name = models.CharField(max_length=50)
    price = models.IntegerField()
    shop = models.ForeignKey(Shop, on_delete = models.CASCADE)
    category = models.CharField(max_length = 254, null=True, choices= CATEGORY)
    brand = models.CharField(max_length = 254)
    barcode = models.CharField(max_length=100, unique=True, default=False)
    description = models.CharField(max_length = 254)
    picture = models.ImageField(upload_to="prodimg", default="")

    def __str__(self):
        return self.name

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shop= models.ForeignKey(Shop, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    barcode = models.CharField(max_length=100, unique=True)

# the unique_together constraint in the CartItem model ensures that 
# each barcode can only be used once for each shop, which should prevent duplicate entries.
    def __str__(self):
        return self.name


    
class Item(models.Model):
    CATEGORY = (
        ('Kitchen','Home appliance'),
        ('Cloths','Shoes'),
        ('electricals','non electric'),
    )
    name = models.CharField(max_length=100)
    shop_id = models.ForeignKey(Shop, on_delete = models.CASCADE)
    category = models.CharField(max_length = 254, null=True, choices= CATEGORY)
    brand = models.CharField(max_length = 254,default = "" )
    quantity = models.CharField(max_length = 254, default = "")
    barcode = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='item_images', null=True, blank=True)

    def __str__(self):
        return self.name