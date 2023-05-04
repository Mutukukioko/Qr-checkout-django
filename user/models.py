from django.db import models
from django.contrib.auth.models import User, AbstractBaseUser, BaseUserManager

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
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, default="")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    barcode = models.CharField(max_length=100, unique=True)
    qr_code = models.ImageField(upload_to='qr_codes', blank=True, null=True)
    added_at =models.DateTimeField(default=timezone.now)

# the unique_together constraint in the CartItem model ensures that 
# each barcode can only be used once for each shop, which should prevent duplicate entries.
    def __str__(self):
        return self.name



class Repo(models.Model):
    
    name = models.CharField(max_length=100, default="")
    shop = models.ForeignKey(Shop, on_delete = models.CASCADE,default="")
    category = models.CharField(max_length = 254,default="")
    brand = models.CharField(max_length = 254,default = "" )
    quantity = models.CharField(max_length = 254, default = "")
    barcode = models.CharField(max_length=100, unique=True, default="")
    price = models.DecimalField(max_digits=8, decimal_places=2,default="")
    image = models.ImageField(upload_to='item_images', null=True, blank=True)

    def __str__(self):
        return self.name




class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('The Email field must be set')
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email=self.normalize_email(email), password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser):
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

class PasswordResetToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)