from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.shortcuts import HttpResponseRedirect
from django.contrib import messages
from .forms import *
from .models import *
from itertools import groupby
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
    return render(request, 'user/home.html', {'title': 'Home'})


@login_required(login_url='/signin')
def admin_home(request):
    return render(request, 'user/home2.html', {'title': 'Home'})


def signin(request):
    # return render(request, 'user/signin.html')
    if request.method == 'POST':

        # AuthenticationForm_can_also_be_used

        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            form = login(request, user)
            messages.success(request, f' welcome {username} !!')
            return redirect('home')
        else:
            messages.info(request, f'account does not exit plz sign in')
    form = AuthenticationForm()
    return render(request, 'user/signin.html', {'form': form, 'title': 'log in'})


# User cart start instance
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
    return render(request, 'user/dashboard.html', {'title': 'Dashboard', 'products': products})


@login_required(login_url='/signin')
def cartdash(request):
    carts = Cart.objects.all()
    return render(request, 'user/cartdash.html', {'title': 'Dashboard', 'carts': carts})


@login_required(login_url='/signin')
def shopProduct(request):
    products = Product.objects.all()
    return render(request, 'user/shop_product.html', {'title': 'Shopproducts', 'products': products})




@login_required(login_url='/signin')
def start_session_view(request):
    if 'shop_id' in request.session and request.session['shop_id'] != shop_id:
        messages.error(
            request, "You cannot scan another shops qr while another shops session is ongoing.")
        return redirect('scanStore')
    if request.method == 'POST':
        # Check if user has an ongoing session for a different shop

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

@login_required(login_url='/signin')
def userBarcode(request):
    if not request.session.get('shop_scanned', False):
        return redirect('scanStore')
    else:
        shop = Shop.objects.get(id=request.session['shop_id'])
        shop_name = shop.shop_name
        form = ItemForm()
        context = {'shop_name': shop_name,'form': form, "shop_image":shop.logo}
        
        return render(request, 'user/user_barcode.html', context)

@login_required(login_url='/signin')
def scanStore(request):
    if 'shop_id' in request.session:
        form = ItemForm()
        context = {'form': form,}
        return render(request, 'user/scan_store.html', context)
    else:
        form = ItemForm()
        return render(request, 'user/scan_store.html', {'form': form})


#view cart items page
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

    return render(request, 'user/cart.html', context)


#storing products into items
@login_required(login_url='/signin')
def store_cart(request):
    # Get the product from the POST request using the barcode
    barcode = request.POST.get('barcode')
    try:
        product = Product.objects.get(barcode=barcode)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'})

    # Get the cart from the session
    cart = request.session.get('cart', {})

    # Convert the product object to a dictionary
    product_dict = {'id': product.id, 'name': product.name, 'price': product.price, 'image': str(product.picture)}

    # Add the product to the cart or increase the quantity if it's already in the cart
    cart_item = cart.get(str(product.name))
    if cart_item is None:
        cart[product.name] = {'product': product_dict, 'quantity': 1, 'barcodes': [barcode]}
    else:
        cart_item['quantity'] += 1
        cart_item['barcodes'].append(barcode)

    # Save the cart to the session
    request.session['cart'] = cart
    return JsonResponse({'success': True})


@login_required(login_url='/signin')
def add(request):
    if 'cart' in request.session:
        cart = request.session.get('cart', {})
        cart_items = []

        for cart_item in cart.values():
            product = cart_item['product']
            cart_items.append({
                'product': Product.objects.get(id=product['id']),
                'quantity': cart_item['quantity'],
                'barcodes': cart_item['barcodes']
            })

        context = {'cart_items':cart_items}
        return render(request, 'user/add.html', context)

    else:
        return render(request, 'user/add.html')



def generate_barcode(request):
    if request.method == 'POST':
        form = Product_Form(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product saved successfully!')
            return redirect('/barcode/')
        else:
            messages.error(
                request, 'Failed to save product. Please check the form data.')
    else:
        form = Product_Form()
    return render(request, 'user/barcode.html', {'form': form})


@login_required(login_url='/signin')
def remove_item(request):
    if request.method == 'POST':
        # Get the product ID and barcode from the POST request
        product_name = request.POST.get('product_name')
        barcode = request.POST.get('barcode')

        # Get the cart from the session
        cart = request.session.get('cart', {})

        # Get the cart item to remove
        cart_item = cart.get(str(product_name))
        if cart_item is None:
            return JsonResponse({'error': 'Cart item not found'})

        # Remove the barcode from the list of barcodes
        cart_item['barcodes'].remove(barcode)

        # If there are no more barcodes for this item, remove the cart item entirely
        if len(cart_item['barcodes']) == 0:
            del cart[product_name]
        else:
            # Otherwise, reduce the quantity by one
            cart_item['quantity'] -= 1

    # Save the cart to the session

            # Save the cart to the session
            request.session['cart'] = cart
            response_data={
                'success': True,
                'message': 'Successfully removed product',
                }

            # Return a success response
            return JsonResponse(response_data)

    # Return an error response if the request is not a POST request or if the cart item does not exist
    response_data = {'error': 'Cart item not found'}
    return JsonResponse(response_data)





@login_required(login_url='/signin')
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
                'message': 'Invalid qr please scan again'
            }
    return JsonResponse(result)


# Compare the barcode input values if they match with existing values in the database
@login_required(login_url='/signin')
def check_prod(request):
    qr_input = request.GET.get('qr_input')
    if not qr_input or qr_input.strip() == '':
        result = {'message': 'Please scan valid Barcode code'}
    else:
        try:
            prod = Product.objects.get(barcode=qr_input)
            if 'shop_id' in request.session:
                shop_id = request.session['shop_id']
                shop = Shop.objects.get(id=shop_id)
                if prod.shop == shop:
                    result = {
                        'success': True,
                        'message': 'add to cart',
                        'exists': True,
                        'name': prod.name,
                    }
                else:
                    result = {
                        'exists': False,
                        'message': 'This product does not belong to the shop in session'
                    }
            else:
                result = {
                    'exists': False,
                    'message': 'Please select a shop to continue'
                }
        except Product.DoesNotExist:
            result = {
                'exists': False,
                'message': 'invalid barcode please scan again'
            }
    return JsonResponse(result)


@login_required(login_url='/signin')
def add_shop(request):
    if request.method == 'POST':
        form = Shop_Form(request.POST, request.FILES)
        if form.is_valid():
            shop = form.save()
            return HttpResponse(status=200)
            # redirect('shop_detail', shop.id)
    else:
        form = Shop_Form()
    return render(request, 'user/addshop.html', {'form': form})


@login_required(login_url='/signin')
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


# Removing the shops session
@login_required(login_url='/signin')
def shop_signout(request):
    shop_name = request.session.get('shop_name')
    if shop_name:
        del request.session['shop_id']
        del request.session['shop_name']
        del request.session['shop_image']
        return redirect('scanStore')
    messages.success(
        request, f"You have successfully signed out of {shop_name}!")


@login_required(login_url='/signin')
def paymentVal(request):
    return render(request, 'user/payment_validation.html')

@login_required(login_url='/signin')
def shop_detail(request, shop_id):
    # Retrieve the Shop object from the database using the shop_id parameter
    shop = Shop.objects.get(id=shop_id)
    return render(request, 'user/shop_detail.html', {'shop': shop})

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
