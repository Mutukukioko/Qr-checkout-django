from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.shortcuts import HttpResponseRedirect
from django.contrib import messages
from .forms import CustomUserCreationForm, ItemForm
from .models import *
import barcode
from django.views import View
from barcode.writer import ImageWriter




def signup(request):
    # return render(request, 'user/signup.html')
    if request.user.is_authenticated:
        return redirect('signin')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            # login(request, user)
            return redirect('signin')
        else:
            return render(request, 'user/signup.html', {'form': form})
    else:
        form = CustomUserCreationForm()
        return render(request, 'user/signup.html', {'form': form})
        

def profile(request): 
    form = CustomUserCreationForm()
    return render(request, 'user/profile.html', {'form': form})


def home(request): 
    return render(request, 'user/home.html',{'title':'Home'})

def signin(request):
    # return render(request, 'user/signin.html')
    if request.method == 'POST':

        #AuthenticationForm_can_also_be_used__

        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            form = login(request,user)
            messages.success(request, f' welcome {username} !!')
            return redirect('home')
        else:
            messages.info(request, f'account does not exit plz sign in')
    form = AuthenticationForm()
    return render(request, 'user/signin.html', {'form':form,'title':'log in'})

def cart(request):
     products = Product.objects.all()
     return render(request, 'user/cart.html',{'title':'cart', 'products':products})

def dashboard(request):
    products = Product.objects.all()
    return render(request, 'user/dashboard.html',{'title':'Dashboard','products':products})

def cartdash(request):
    carts = CartItem.objects.all()
    return render(request, 'user/cartdash.html',{'title':'Dashboard','carts':carts})




def add(request):
    if request.method == 'POST':
        form = Product(request.POST, request.FILES)
 
        if form.is_valid():
            form.save()
            return redirect('success')
    else:
        form = Product()
 
    return render(request, 'user/add.html',{'form': form,'title':'add'})


class ScanView(View):
    template_name = 'user/barcode.html'

    def get(self, request):
        form = ItemForm()
        return render(request, self.template_name, {'form': form})

class ResultView(View):
    def post(self, request):
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.barcode = request.POST['barcode']
            item.save()
            return HttpResponseRedirect('/barcode/')
        return render(request, 'user/barcode.html', {'form': form})


def shopProduct(request):
    products = Product.objects.all()
    return render(request, 'user/shop_product.html', {'title':'Shopproducts','products':products})

def userBarcode(request):
    form = ItemForm()
    return render(request, 'user/user_barcode.html',{'form': form})

def paymentVal(request):
    return render(request, 'user/payment_validation.html')

def scanStore(request):
    form = ItemForm()
    return render(request, 'user/scan_store.html', {'form': form})
