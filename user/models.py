from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone





class Shop(models.Model):
    name = models.CharField(max_length=50,default='user')
    user = models.OneToOneField(User, on_delete=models.CASCADE,default="user")
    location = models.CharField(max_length=50)
    image = models.ImageField(upload_to='shop_images/', default="")
    qrcode = models.ImageField(upload_to='shop_qrcodes/', default="")
    

    def __str__(self):
        return self.name

class Product(models.Model):
    CATEGORY = (
        ('Kitchen','Home appliance'),
        ('Cloths','Shoes'),
        ('electricals','non electric'),
    )
    name = models.CharField(max_length=50)
    price = models.IntegerField()
    user = models.ForeignKey(User, on_delete = models.CASCADE, default="")
    category = models.CharField(max_length=254, null=True, choices=CATEGORY)
    brand = models.CharField(max_length=254)
    barcode = models.CharField(max_length=100, unique=True, default=False)
    description = models.CharField(max_length=254)
    picture = models.ImageField(upload_to="prodimg", default="")

    def __str__(self):
        return self.name

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart_id = models.UUIDField(default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    barcode = models.CharField(max_length=100, unique=True)
    qr_code = models.ImageField(upload_to='qr_codes', blank=True, null=True)
    added_at =models.DateTimeField(default=timezone.now)

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
    shop = models.ForeignKey(Shop, on_delete = models.CASCADE)
    category = models.CharField(max_length = 254, null=True, choices= CATEGORY)
    brand = models.CharField(max_length = 254,default = "" )
    quantity = models.CharField(max_length = 254, default = "")
    barcode = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='item_images', null=True, blank=True)

    def __str__(self):
        return self.name





class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(blank=True, null=True)


