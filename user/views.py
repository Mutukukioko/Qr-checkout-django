from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.shortcuts import HttpResponseRedirect
from django.contrib import messages
from .forms import *
from .models import *
import qrcode
from django.http import HttpResponse, JsonResponse
from django.views import View
from barcode.writer import ImageWriter
from django.contrib.auth.decorators import login_required

def logout_view(request):
    logout(request)
    return redirect('signin')

def signup(request):
    # return render(request, 'user/signup.html')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data.get('email')
            user.save()
            messages.success(request, f'Account created for {user.username}!')
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
    if 'cart' in request.session:
        cart = request.session['cart']
        cart_items = []
        
        for product_id, item in cart.items():
            product = Product.objects.get(id=product_id)
            cart_item = {
                'prod_id':product_id,
                'product': product,
                'quantity': item['quantity']
            }
            cart_items.append(cart_item)

        context = {'cart_items': cart_items}
        return render(request,'user/add.html',context)
    
    else:
        return render(request,'user/add.html')

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
    if not request.session.get('shop_scanned', False):
        return redirect('scanStore')
    form = ItemForm()
    return render(request, 'user/user_barcode.html',{'form': form})

def paymentVal(request):
    return render(request, 'user/payment_validation.html')

def scanStore(request):
    form = ItemForm()
    return render(request, 'user/scan_store.html', {'form': form})

@login_required(login_url='/signin')  
def view_cart(request):
    cart_items = []
    cart = request.session.get('cart', {})
    for product_id, item in cart.items():
        product = Product.objects.get(id=product_id)
        cart_item = {
            'product': product,
            'quantity': item['quantity']
        }
        cart_items.append(cart_item)

        context = {'cart_items': cart_items}
    
    return render(request, 'user/cart.html',context)
         
  
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
            response_data = {'status': 'success', 'message': 'Item removed!'}
            return JsonResponse(response_data)

        else:
            response_data = {'status': 'error', 'message': 'Item not found!'}
            return JsonResponse(response_data)

    else:
        return redirect('add')

def start_session_view(request):
    if request.method == 'POST':
        shop_id = request.POST.get('shop_id')
        # Query the database to check if the shop ID exists
        try:
            shop = Shop.objects.get(id=shop_id)
        except Shop.DoesNotExist:
            # Return an error message if the shop ID doesn't exist
            return JsonResponse({'success': False, 'message': 'Invalid shop ID'})

        # Set the shop ID in the session
        request.session['shop_id'] = shop_id
        request.session['shop_name'] = shop.shop_name
        request.session['shop_image'] = str(shop.logo)

        # Set the flag to indicate that the shop ID has been scanned
        request.session['shop_scanned'] = True

        return JsonResponse({'success': True, 'message': 'Shop scanned successfully'})

    else:
            return JsonResponse({'error': 'Invalid request method'})


def check_shop(request):
    qr_input = request.GET.get('qr_input')
    if not qr_input or qr_input.strip() == '':
        result = {'message': 'Please scan valid QR code'}
    else:
        try:
            shop = Shop.objects.get(id=qr_input)
            result = {

                'success': True,
                'message': 'Shop details retrieved successfully',
                'exists': True,
                'name': shop.shop_name,
                'image': shop.logo.url,
            }
        except Shop.DoesNotExist:
            result = {
                'exists': False,
                'message':'Invalid qr please scan again'
            }
    return JsonResponse(result)

def check_prod(request):
    qr_input = request.GET.get('qr_input')
    if not qr_input or qr_input.strip() == '':
        result = {'message': 'Please scan valid Barcode code'}
    else:
        try:
            prod = Product.objects.get(id=qr_input)
            result = {

                'success': True,
                'message': 'add to cart',
                'exists': True,
                'name': prod.name,
            }
        except Product.DoesNotExist:
            result = {
                'exists': False,
                'message':'invalid barcode please scan again'
                }
    return JsonResponse(result)


def add_shop(request):
    if request.method == 'POST':
        form = Shop_Form(request.POST, request.FILES)
        if form.is_valid():
            shop = form.save()
            return HttpResponse(status = 200)
            # redirect('shop_detail', shop.id)
    else:
        form = Shop_Form()
    return render(request, 'user/addshop.html', {'form': form})
        


def shop_detail(request, shop_id):
    # Retrieve the Shop object from the database using the shop_id parameter
    shop = Shop.objects.get(id=shop_id)
    return render(request, 'user/shop_detail.html', {'shop': shop})



def generate_qrcode(request):
    if request.method == 'POST':
        data = request.POST.get('data')
        img = qrcode.make(data)
        img_path = 'media/qrcodes/' + data + '.png'
        img.save(img_path)
        context = {'qr_code_path': img_path}
        return render(request, 'user/qrcode.html', context)
    else:
        return render(request, 'user/generate_qrcode.html')

def shop_signout(request):
    shop_name = request.session.get('shop_name')
    if shop_name:
        del request.session['shop_id']
        del request.session['shop_name']
        del request.session['shop_image']
        return redirect('scanStore')
        messages.success(request, f"You have successfully signed out of {shop_name}!")
    





            