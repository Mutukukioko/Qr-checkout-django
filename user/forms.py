from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Product, Cart, CartItem, Shop, Item


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model=User
        fields=['first_name','email','username','password1','password2']
        
    def __init__(self,*args, **kwargs):
        super(UserCreationForm,self).__init__(*args, **kwargs)
        for name,field in self.fields.items():
            field.widget.attrs.update({'class':'input'})


class Product_Form(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"


        
    


class Cart_Form(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = Cart
        fields = "__all__"

class CartItem_Form(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = "__all__"


class Shop_Form(forms.ModelForm):
    class Meta:
        model = Shop
        fields = "__all__"


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = "__all__"