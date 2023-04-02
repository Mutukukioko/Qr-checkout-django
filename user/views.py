from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.shortcuts import HttpResponseRedirect
from django.contrib import messages
from .forms import CustomUserCreationForm, ItemForm
from .models import *
from django.http import HttpResponse
from django.views import View
from barcode.writer import ImageWriter
from django.contrib.auth.decorators import login_required

def logout_view(request):
    logout(request)
    return redirect('signin')

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
        
@login_required(login_url='/signin')
def profile(request): 
    if request.user.is_authenticated:
        # If the user is authenticated, show their details
        username = request.user.username
        first_name = request.user.first_name
        last_name = request.user.last_name
        email = request.user.email
        return render(request, 'user/profile.html', {
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
        })
    else:
        # If the user is not authenticated, redirect them to the login page
        return redirect('signin')


@login_required(login_url='/signin')
def home(request): 
    return render(request, 'user/home.html',{'title':'Home'})

@login_required(login_url='/signin')
def admin_home(request): 
    return render(request, 'user/home2.html',{'title':'Home'})


def signin(request):
    # return render(request, 'user/signin.html')
    if request.method == 'POST':

        #AuthenticationForm_can_also_be_used

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

@login_required(login_url='/signin')
def cart(request):
    cart = request.session.get('cart', {})
    barcode = cart.get('barcode', '')
    context = {
        'barcode': barcode,
        'cart_items': cart.items()
    }
    return render(request, 'user/cart.html', context)

@login_required(login_url='/signin')
def dashboard(request):
    products = Product.objects.all()
    return render(request, 'user/dashboard.html',{'title':'Dashboard','products':products})


@login_required(login_url='/signin')
def cartdash(request):
    carts = CartItem.objects.all()
    return render(request, 'user/cartdash.html',{'title':'Dashboard','carts':carts})



@login_required(login_url='/signin')
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


@login_required(login_url='/signin')
def shopProduct(request):
    products = Product.objects.all()
    return render(request, 'user/shop_product.html', {'title':'Shopproducts','products':products})

@login_required(login_url='/signin')
def userBarcode(request):
    form = ItemForm()
    return render(request, 'user/user_barcode.html',{'form': form})

def paymentVal(request):
    return render(request, 'user/payment_validation.html')

def scanStore(request):
    form = ItemForm()
    return render(request, 'user/scan_store.html', {'form': form})


@login_required(login_url='/signin')
def add_cart (request, item_id):
    if request.user.is_authenticated:
        # retrieve the cart from the session or create a new one
        cart = Cart.objects.filter(user=request.user)
        cart = request.session.get('cart', {})
        
         # add the item to the cart or update the quantity if already in the cart
        cart[item_id] = cart.get(item_id, 0) + 1
        
       
  # save the updated cart to the session
        request.session['cart'] = cart

    # redirect to the cart page
        return render(request, 'user/add.html', {'cart': cart})

    else:
        # handle the case where the user is not logged in
        return render(request, 'user/home.html', {'cart': cart})
   
    

@login_required(login_url='/signin')  
def view_cart(request):
    cart_items = []
    cart = request.session.get('cart', {})
    for barcodevalue, item in cart.items():
        cart_item = {
            'barcodevalue': barcodevalue,
            'quantity': item['quantity']
        }
        cart_items.append(cart_item)
    # render the cart template with the cart items
    return render(request, 'user/cart.html', {'cart': cart_items})
         
  
def store_cart(request):
    cart = request.session.get('cart', {})
    barcodevalue = request.POST.get('barcode')
    if barcodevalue:
        if barcodevalue in cart:
            # if the barcode value already exists in the cart, increment its quantity
            cart[barcodevalue]['quantity'] += 1
        else:
            # if it doesn't exist, add it to the cart with a quantity of 1
            cart[barcodevalue] = {'quantity': 1}
    request.session['cart'] = cart
    return  HttpResponse(status = 200)


    

    # return render(request, 'user/home.html')
    
def generate_barcode(request):
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.barcode = request.POST['barcode']
            item.save()
            return HttpResponseRedirect('/barcode/')
        return render(request, 'user/barcode.html', {'form': form})


def remove_item(request):
    if request.method == "POST":
        barcode_value = request.POST.get("barcode_value")
        if barcode_value in request.session["cart"]:
            del request.session["cart"][barcode_value]
            request.session.modified = True
            messages.success(request, f' item removed!!')
    return redirect('view_cart')

