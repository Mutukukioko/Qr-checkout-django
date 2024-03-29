from base64 import urlsafe_b64decode
from datetime import date,timedelta
from email.message import EmailMessage
import os
import smtplib
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.shortcuts import HttpResponseRedirect
from django.contrib import messages
from .forms import *
from .models import *
import uuid
from django.db.models import Count, Sum
from django.db import transaction
import qrcode
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from io import BytesIO
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required, user_passes_test
from .utils import specific_superuser_required
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db.models import Avg
from django.db.models.functions import TruncMonth, TruncWeek
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail
from django.conf import settings


def logout_view(request):
    logout(request)
    messages.success(request,'Logged out successsfully')
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


def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_superuser and user.username == 'mutuku':
                login(request, user)
                messages.success(request, f'Welcome {username} (Superuser)!')
                return redirect('add_shop')
            elif user.is_superuser:
                login(request, user)
                messages.success(request, f'Welcome {username} (Superuser)!')
                return redirect('admin_home')
            else:
                login(request, user)
                messages.success(request, f'Welcome {username}!')
                return redirect('home')
        else:
            messages.info(request, f'Account does not exist. Please sign in.')

    form = AuthenticationForm()
    return render(request, 'user/signin.html', {'form': form, 'title': 'Log in'})


@login_required(login_url='/signin')
def update_profile(request):
    user = request.user
    if request.method == 'POST':
        # Get the data from the AJAX request
        first_name = request.POST.get('first_name')
        username = request.POST.get('username')
        email = request.POST.get('email')

        # Get the current user
        user = request.user

        # Update the user's profile information
        user.first_name = first_name
        user.username = username
        user.email = email
        user.save()

    # Return a success JSON response
    return JsonResponse({'success': True})


@login_required(login_url='/signin')
def home(request):
    user_id = request.user.id
    # get the number of unique cart ids for a specific user
    unique_cart = Cart.objects.filter(
        user_id=user_id).values('cart_id').distinct().count()

    return render(request, 'user/home.html', {'title': 'Home', 'count': unique_cart})



@login_required(login_url='/signin')
@specific_superuser_required(username='my_specific_superuser_username')
def add_shop(request):
    if request.method == 'POST':
        # create the user account for the shop owner
        username = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']

        # check if the username and email are unique
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken')
            return redirect('add_shop')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already taken')
            return redirect('add_shop')

        user = User.objects.create_superuser(
            username=username, email=email, password=password)

        # create the shop object
        name = request.POST['name']
        location = request.POST['location']
        image = request.FILES['image']
        shop = Shop.objects.create(
            name=name, location=location, user=user, image=image)

        # generate the QR code
        qr = qrcode.QRCode(
            version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(f"{name} - {location}")
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # save the QR code image to the shop object
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        image_file = ContentFile(buffer.getvalue())
        filename = f"{name.replace(' ', '_')}_{location.replace(' ', '_')}.png"
        file_path = f"qrcodes/{filename}"
        default_storage.save(file_path, image_file)
        shop.qrcode.save(filename, image_file)
        messages.success(request, 'The Shop has been successfully saved to the database')


    else:

        return render(request, 'user/addshop.html')

# ____________________________ADMIN________________________
    # Admin home page
@login_required(login_url='/signin')
@user_passes_test(lambda u: u.is_superuser)
def admin_home(request):
    userid = request.user
    # get the number of unique cart ids for a specific user
    unique_products = Product.objects.filter(
        user_id=userid).values('id').distinct().count()
    
    shop=Shop.objects.get(user_id=request.user)
    total_sales =Cart.objects.filter(
        shop_id=shop.id).values('cart_id').distinct().count()
    
    context = {'title': 'Home',
               'items':unique_products,
                'totals':total_sales,
                'image':shop.image.url,
                }
    return render(request, 'user/home2.html', context )

# Shops Details
@login_required(login_url='/signin')
@user_passes_test(lambda u: u.is_superuser)
def shop_profile(request):
    if request.user.is_authenticated:
        # If the user is authenticated, show their details
        username = request.user.username
        email = request.user.email
        shop=Shop.objects.get(user_id=request.user)
        data = {
            'username': username,
            'email': email,
            'name':shop.name,
            'location':shop.location,
            'image':shop.image.url,
            'qrcode':shop.qrcode.url,
        }
        return render(request, 'user/shop_profile.html', data)
    else:
        # If the user is not authenticated, redirect them to the login page
        return redirect('signin')

# Admin Cartlogs
@login_required(login_url='/signin')
@user_passes_test(lambda u: u.is_superuser)
def cartdash(request):
    shop=Shop.objects.get(user_id=request.user)

    carts = Cart.objects.filter(shop_id=shop.id)
    context = {'title': 'Dashboard',
            'carts': carts,
            'username': request.user.username,
            'image':shop.image.url,
        }
    return render(request, 'user/cartdash.html', context)

# Admin product dashboard
@login_required(login_url='/signin')
@user_passes_test(lambda u: u.is_superuser)
# group products by description and count how many have the same description
def shopProduct(request):
    # get current user
    user = request.user
    #get count of products 
    
    product = Product.objects.filter(user_id=user.id).annotate(total=Count('description')) \
        .order_by('-total')
    
    shop=Shop.objects.get(user_id=request.user)
    context = {
        'title': 'Shopproducts', 
        'product':product,
        'username': request.user.username,
        'image':shop.image.url,
        }
    return render(request, 'user/shop_product.html',context)

# scan the User generated Qr
@login_required(login_url='/signin')
@user_passes_test(lambda u: u.is_superuser)
def scanQr(request):
    shop=Shop.objects.get(user_id=request.user)
    context = {
        'title': 'Scan Qr', 
        'username': request.user.username,
        'image':shop.image.url,
        }
    return render(request, 'user/scanQr.html', context)

# add products to product table
@login_required(login_url='/signin')
@user_passes_test(lambda u: u.is_superuser)
def generate_barcode(request):
    if request.method == 'POST':
        name = request.POST['name']
        price = request.POST['price']
        category = request.POST['category']
        brand = request.POST['brand']
        barcode = request.POST['barcode']
        description = request.POST['description']
        picture = request.FILES.get('picture')

        # get current user
        user = request.user
# check if the barcode already exists
        if Product.objects.filter(barcode=barcode).exists():
            messages.error(request, 'Product with the given barcode already exists')
            return redirect('barcode_scanner')
        else:
            # create new product
            product = Product(name=name, price=price, category=category, brand=brand, barcode=barcode, description=description, picture=picture, user=user)
            product.save()

            messages.success(request, 'Product has been added successfully')
            form = Product_Form()
            return render(request, 'user/barcode.html', {'form': form})
            
    else:
        shop=Shop.objects.get(user_id=request.user)
        form = Product_Form()
        context = {
            'title': 'Scan Qr', 
            'username': request.user.username,
            'image':shop.image.url,
            'form': form
            }
        return render(request, 'user/barcode.html', context)



@login_required(login_url='/signin')
@user_passes_test(lambda u: u.is_superuser)
def sales_analytics(request):
    shop=Shop.objects.get(user_id=request.user)
    # Get daily sales data

    daily_sales = Cart.objects.filter(
        added_at__date=date.today(),
        shop_id=shop.id
    ).aggregate(
        total_sales=Sum('product__price'),
        num_sales=Count('id')
    )

    # Get weekly sales data
    week_ago = date.today() - timedelta(days=7)
    weekly_sales = Cart.objects.filter(
        shop_id=shop.id,
        added_at__date__gte=week_ago,
        added_at__date__lte=date.today()
    ).aggregate(
        total_sales=Sum('product__price'),
        num_sales=Count('id')
    )

    # Get monthly sales data
    month_ago = date.today() - timedelta(days=30)
    monthly_sales = Cart.objects.filter(
        shop_id=shop.id,
        added_at__date__gte=month_ago,
        added_at__date__lte=date.today()
    ).aggregate(
        total_sales=Sum('product__price'),
        num_sales=Count('id')
    )

    # Get average basket size for today
    today_avg_basket_size = Cart.objects.filter(
        shop_id=shop.id,
        added_at__date=date.today()
    ).aggregate(
        avg_basket_size=Avg('cart_id', distinct=True)
    )

    # Get average basket size for this week
    weekly_avg_basket_size = Cart.objects.filter(
        shop_id=shop.id,
        added_at__date__gte=week_ago,
        added_at__date__lte=date.today()
    ).annotate(
        week=TruncWeek('added_at')
    ).values('week').annotate(
        avg_basket_size=Avg('cart_id', distinct=True)
    )

    # Get average basket size for this month
    month_ago = date.today() - timedelta(days=180)
    monthly_avg_basket_size = Cart.objects.filter(
        shop_id=shop.id,
        added_at__date__gte=month_ago,
        added_at__date__lte=date.today()
    ).annotate(
        month=TruncMonth('added_at')
    ).values('month').annotate(
        avg_basket_size=Avg('cart_id', distinct=True)
    )

    # Get data for the current month only
    current_month = timezone.now().month
    current_month_data = monthly_avg_basket_size.filter(month__month=current_month)

    # Exclude the current month from the main data
    monthly_avg_basket_size = monthly_avg_basket_size.exclude(month__month=current_month)


    # Get top selling products
    top_selling_products = Cart.objects.filter(shop_id=shop.id).values('product_id', 'product__name', 'product__picture', 'product__price') \
    .annotate(total_sales=Count('product_id')) \
    .order_by('-total_sales')[:10]
    shop=Shop.objects.get(user_id=request.user)
    
    context = {
        'daily_sales': daily_sales,
        'weekly_sales': weekly_sales,
        'monthly_sales': monthly_sales,
        'today_avg_basket_size': today_avg_basket_size,
        'weekly_avg_basket_size': weekly_avg_basket_size,
        'monthly_avg_basket_size': monthly_avg_basket_size,
        'top_selling_products': top_selling_products,
        'title': 'Shopproducts', 
        'username': request.user.username,
        'image':shop.image.url,
    }

    return render(request, 'user/sales_analytics.html', context)

#sales analysis
def sales_analysis(request):
    # Aggregate sales data for each category
    category_sales = Cart.objects.values('product__category').annotate(
        total_sales=Sum('product__price'),
        num_sales=Count('id')
    )

    # Aggregate sales data for each brand
    brand_sales = Cart.objects.values('product__brand').annotate(
        total_sales=Sum('product__price'),
        num_sales=Count('id')
    )

    # Aggregate sales data for each product
    product_sales = Cart.objects.values('product__name').annotate(
        total_sales=Sum('product__price'),
        num_sales=Count('id')
    )
    shop=Shop.objects.get(user_id=request.user)
    context = {
        'title': 'Scan Qr', 
        'username': request.user.username,
        'image':shop.image.url,
        'category_sales': category_sales,
        'brand_sales': brand_sales,
        'product_sales': product_sales
    
        }
    # Render the template with the sales data
    return render(request, 'user/sales_analysis.html',context)


# ________________USER____________________

    # This is where the user starts his shopping session
@login_required(login_url='/signin')
@user_passes_test(lambda u: not u.is_superuser, login_url='/signin')
def start_session_view(request):
    if request.method == 'POST':
        shop_name = request.POST.get('shop_name')
        # Query the database to check if the shop ID exists
        try:
            shop = Shop.objects.get(name=shop_name)
        except Shop.DoesNotExist:
            # Return an error message if the shop ID doesn't exist
            return JsonResponse({'success': False, 'message': 'Invalid shop ID'})

        if 'shop_name' in request.session and request.session['shop_name'] != shop_name:
            messages.error( request, "You cannot scan another shop's QR while another shop's session is ongoing.")
            return redirect('scanStore')
        
        # Set the shop ID in the session
        request.session['shop_id'] = shop.user.id
        request.session['shop_name'] = shop.name
        request.session['shop_image'] = str(shop.image)

        # Set the flag to indicate that the shop ID has been scanned
        request.session['shop_scanned'] = True

        return JsonResponse({'success': True, 'message': 'Shop scanned successfully'})

    else:
        return JsonResponse({'error': 'Invalid request method'})


# scan product barcode
@login_required(login_url='/signin')
@user_passes_test(lambda u: not u.is_superuser, login_url='/signin')
def userBarcode(request):
    if not request.session.get('shop_scanned', False):
        return redirect('scanStore')
    else:
        shop = Shop.objects.get(user_id=request.session['shop_id'])
        shop_name = shop.name
        form = ItemForm()
        context = {'shop_name': shop_name,
                   'form': form, "shop_image": shop.image, 'shopid':request.session['shop_id']}

        return render(request, 'user/user_barcode.html', context)


@login_required(login_url='/signin')
@user_passes_test(lambda u: not u.is_superuser, login_url='/signin')
def scanStore(request):
    if 'shop_id' in request.session:
        form = ItemForm()
        context = {'form': form, }
        return render(request, 'user/scan_store.html', context)
    else:
        form = ItemForm()
        return render(request, 'user/scan_store.html', {'form': form})


# view cart items page
@login_required(login_url='/signin')
@user_passes_test(lambda u: not u.is_superuser, login_url='/signin')
def view_cart(request):
    cart_items = []
    cart = request.session.get('cart', {})
    for product_name, item in cart.items():
        product_dict = item['product']
        product_dict['name'] = product_name
        cart_item = {
            'product': product_dict,
            'quantity': item['quantity'],
            'total_price': item['quantity'] * product_dict['price'],
        }
        cart_items.append(cart_item)

    context = {'cart_items': cart_items}

    return render(request, 'user/cart.html', context)


# storing products into cart
@login_required(login_url='/signin')
@user_passes_test(lambda u: not u.is_superuser, login_url='/signin')
def store_cart(request):
    # Get the product from the POST request using the barcode
    barcode = request.POST.get('barcode')
    try:
        product = Product.objects.get(barcode=barcode)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'})

    # Get the cart from the session
    cart = request.session.get('cart', {})

    # Check if the product is already in the cart
    for cart_item in cart.values():
        if barcode in cart_item['barcodes']:
            return JsonResponse({'error': 'Product already in cart'})

    # Convert the product object to a dictionary
    product_dict = {'id': product.id, 'name': product.name,
                    'price': product.price, 'image': str(product.picture)}

    # Add the product to the cart or increase the quantity if it's already in the cart
    cart_item = cart.get(str(product.name))
    if cart_item is None:
        cart[str(product.name)] = {
            'product': product_dict, 'quantity': 1, 'barcodes': [barcode]}
    else:
        cart_item['quantity'] += 1
        cart_item['barcodes'].append(barcode)

    # Save the cart to the session
    request.session['cart'] = cart
    messages.success(request,'Stored in cart successfully')
    return JsonResponse({'success': True})


# The current view for users cart
@login_required(login_url='/signin')
@user_passes_test(lambda u: not u.is_superuser, login_url='/signin')
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

        context = {'cart_items': cart_items}
        return render(request, 'user/add.html', context)

    else:
        return render(request, 'user/add.html')

# Saving cart to the database


@login_required(login_url='/signin')
@user_passes_test(lambda u: not u.is_superuser, login_url='/signin')
@transaction.atomic
def save_cart(request):
    if request.method == 'POST':
        # Loop through each item in the cart
        all_saved = True
        cart = request.session['cart']
        shop_id = request.session['shop_id']
        shopi = get_object_or_404(Shop, user_id=shop_id)
        # Create a list of products to save
        products_to_save = []
        for cart_item in cart.values():
            for barcode in cart_item['barcodes']:
                product_dict = {'id': cart_item['product']['id'], 'name': cart_item['product']['name'],
                                'price': cart_item['product']['price'], 'image': cart_item['product']['image'],
                                'barcode': barcode}
                products_to_save.append(product_dict)
        cartId = uuid.uuid4()
        # Save the products to the database
        for product_dict in products_to_save:
            product_id = product_dict['id']

            product = get_object_or_404(Product, id=product_id)
            cart_item = Cart(cart_id=cartId, user=request.user,
                             product_id=product.id, barcode=product_dict['barcode'],shop=shopi)

            # Generate QR code and save as Base64 string in the database
            qr_data = f"{cartId} paid"
            qr_code = qrcode.make(qr_data)
            qr_filename = f"{cartId}.png"
            qr_path = os.path.join('media/qr_codes', qr_filename)
            qr_code.save(qr_path)

            cart_item.qr_code.name = qr_filename
            cart_item.save()
            
            all_saved = True

        # Clear the cart
        if all_saved == True:
            request.session['cart'] = {}
            messages.success(request, 'Cart cleared.')
            return redirect('home')
        else:
            messages.warning(request, 'Cart not cleared.')
            return redirect('home')

    else:
        return redirect('add')
# remove cart items from the cart session


@login_required(login_url='/signin')
@user_passes_test(lambda u: not u.is_superuser, login_url='/superuser/dashboardn')
def remove_item(request):
    # Get the product ID and barcode from the POST request
    product_name = request.POST.get('product_name')
    barcode = request.POST.get('barcode')

    # Get the cart from the session
    cart = request.session.get('cart', {})

    # Get the cart item for the product
    cart_item = cart.get(str(product_name))

    # Check if the cart item exists
    if cart_item is None:
        return JsonResponse({'error': 'Product not found in cart'})

    # Check if the barcode is in the list of barcodes for the cart item
    if barcode not in cart_item['barcodes']:
        return JsonResponse({'error': 'Barcode not found in cart item'})

    # If there is only one barcode for the cart item, remove the entire item from the cart
    if len(cart_item['barcodes']) == 1:
        del cart[str(product_name)]
    else:
        cart_item['barcodes'].remove(barcode)
        # Otherwise, reduce the quantity by one
        cart_item['quantity'] -= 1

    # Save the updated cart to the session
    request.session['cart'] = cart

    return JsonResponse({'success': True, 'message': 'success removed cart'})


# Check shop if exists in the database
@login_required(login_url='/signin')
def check_shop(request):
    if request.method == 'GET':
        posted_value = request.GET.get('qr_input')
        if not posted_value or posted_value.strip() == '':
            result = {'message': 'Please scan valid QR code'}
        else:
            try:
                # Retrieve all qr codes from the database
                shops = Shop.objects.all()

                # Compare posted value with truncated values from database
                for shop in shops:
                    full_name = shop.name
                    if posted_value.replace("-", "") == full_name:

                        result = {
                            'success': True,
                            'message': 'Shop details retrieved successfully',
                            'exists': True,
                            'name': shop.name,
                            'image': shop.image.url,
                            # Add other attributes here as needed
                        }
                        break  # Exit the loop if a match is found

                else:
                    result = {
                        'success': False,
                        'message': 'Shop details not found',
                        'exists': False,
                    }
            except Shop.DoesNotExist:
                result = {
                    'exists': False,
                    'message': 'Invalid QR code, please scan again'
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
            shop_id = request.session['shop_id']
            prod = get_object_or_404(Product, barcode=qr_input, user_id=shop_id)
            if prod :
                # shop = Shop.objects.get(user_id=shop_id)
                # if prod.user_id == shop_id:
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
           
        except Product.DoesNotExist:
            result = {
                'exists': False,
                'message': 'invalid barcode please scan again'
            }
    return JsonResponse(result)

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

# user dashboard

@login_required(login_url='/signin')
@user_passes_test(lambda u: not u.is_superuser, login_url='/signin')
def inventory(request):
    user_id = request.user.id
    cart_items = Cart.objects.filter(user_id=user_id)

    # group cart items by product description and calculate total quantity and cost
    product_groups = {}
    for cart_item in cart_items:
        product_desc = cart_item.product.description
        if product_desc not in product_groups:
            product_groups[product_desc] = {
                'quantity': 0,
                'cost': 0,
                'name': '',
                'cart_id': ''
            }
        product_groups[product_desc]['quantity'] += 1
        product_groups[product_desc]['cost'] += cart_item.product.price
        product_groups[product_desc]['image'] = cart_item.product.picture
        product_groups[product_desc]['name'] = cart_item.product.name
        product_groups[product_desc]['cart_id'] = cart_item.cart_id

    # get the number of unique cart ids for a specific user
    unique_cart = Cart.objects.filter(
        user_id=user_id).values('cart_id').distinct().count()

    context = {'product_groups': product_groups, 'Count': unique_cart}
    return render(request, 'user/userInventory.html', context)

# user profile


@login_required(login_url='/signin')
@user_passes_test(lambda u: not u.is_superuser, login_url='/signin')
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






# ____________Not neccessary code but in evaluation_______________________
@login_required(login_url='/signin')
# @user_passes_test(lambda u: u.is_superuser)
def dashboard(request):
    products = Product.objects.all()
    return render(request, 'user/dashboard.html', {'title': 'Dashboard', 'products': products})



@login_required(login_url='/signin')
def generate_qrcode(request):
    if request.method == 'POST':
        data = request.POST.get('data')
        qr = qrcode.QRCode(
            version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(data)
        # img = qrcode.make(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        img_path = 'media/qrcodes/' + data + '.png'
        img.save(img_path)
        context = {'qr_code_path': img_path}
        return render(request, 'user/qrcode.html', context)
    else:
        return render(request, 'user/generate_qrcode.html')


@login_required(login_url='/signin')
def paymentVal(request):
    return render(request, 'user/payment_validation.html')


@login_required(login_url='/signin')
def shop_detail(request, shop_id):
    # Retrieve the Shop object from the database using the shop_id parameter
    shop = Shop.objects.get(id=shop_id)
    return render(request, 'user/shop_detail.html', {'shop': shop})


@login_required(login_url='/signin')
def cart(request):
    cart = request.session.get('cart', {})
    barcode = cart.get('barcode', '')
    context = {
        'barcode': barcode,
        'cart_items': cart.items()
    }
    return render(request, 'user/cart.html', context)


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


class PasswordResetView(View):

    def get(self, request):
        form = PasswordResetForm()
        return render(request, 'user/password_reset_form.html', {'form': form})

    def post(self, request):
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            # Get the user with the specified email address
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()

            if user is not None:
                # Generate a token for the password reset link
                token_generator = PasswordResetTokenGenerator()
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = token_generator.make_token(user)

                # Send the password reset link to the user's email address
                subject = 'Password reset for your account'
                message = f'Please click on the following link to reset your password: {settings.BASE_URL}/reset-password/{uid}/{token}'
                recipient_list = [email]
                smtp_connection = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
                smtp_connection.starttls()
                smtp_connection.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)


                try:
                    email_message = EmailMessage(
                        subject='Password reset for your account',
                        body=f'Please click on the following link to reset your password: {settings.BASE_URL}/reset-password/{uid}/{token}',
                        from_email=settings.EMAIL_HOST_USER,
                        to=[email],
                    )
                    email_message.send()
                    return HttpResponse('Password reset email sent.')
                except Exception as e:
                    print(e)
                    return HttpResponse('An error occurred while sending the password reset email.')

            # Always return a success message to avoid leaking information
            return HttpResponse('Password reset email sent.')

        return render(request, 'user/password_reset_form.html', {'form': form})


class PasswordResetConfirmView(View):

    def get(self, request, uidb64, token):
        try:
            # Decode the user ID from the URL parameter
            uid = urlsafe_b64decode(uidb64).decode('utf-8')

            # Get the user with the specified ID
            user = User.objects.get(pk=uid)

            # Check if the token is valid
            token_generator = PasswordResetTokenGenerator()
            if not token_generator.check_token(user, token):
                return HttpResponseBadRequest('Invalid password reset link.')

            # Display the password reset form
            form = SetPasswordForm(user)
            return render(request, 'user/password_reset_confirm.html', {'form': form})

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return HttpResponseBadRequest('Invalid password reset link.')

    def post(self, request, uidb64, token):
        try:
            # Decode the user ID from the URL parameter
            uid = urlsafe_b64decode(uidb64).decode('utf-8')

            # Get the user with the specified ID
            user = User.objects.get(pk=uid)

            # Check if the token is valid
            token_generator = PasswordResetTokenGenerator()
            if not token_generator.check_token(user, token):
                return HttpResponseBadRequest('Invalid password reset link.')

            # Process the password reset form
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                user = form.save()
                user = authenticate(username=user.username, password=form.cleaned_data['new_password1'])
                login(request, user)
                return HttpResponse('Password reset successful.')
            else:
                return render(request, 'user/password_reset_confirm.html', {'form': form})

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return HttpResponseBadRequest('Invalid password reset link.')




