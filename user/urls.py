from django.urls import path
from . import views
from .views import logout_view
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
path('signin/',views.signin, name='signin'),
path('signup/',views.signup, name='signup'),
path('logout/', logout_view, name='logout'),
#ADMIN
path('home2/',views.admin_home, name="admin_home"),
path('dashboard/', views.dashboard, name='dashboard'),
path('cartdash/', views.cartdash, name = 'cartdash'),
path('scanQr/', views.scanQr, name='scanQr'),
path('shop_profile/',views.shop_profile, name='shop_profile'),
#add shop product
path('barcode/', views.generate_barcode, name='barcode_scanner'),
path('shop_product/', views.shopProduct, name='shopProduct'),
#OTHER Admins
# path('message/<int:shop_id>/', views.message_view, name='message_view'),
# path('message/<int:shop_id>/room/', views.message_room, name='message_room'),
# path('ws/chat/<str:room_name>/', views.ChatConsumer.as_asgi()),

path('sales_analytics/',views.sales_analytics, name='sales_analytics'),
path('addshop/', views.add_shop, name='add_shop'),
path('payment_validation/', views.paymentVal, name='paymentVal'),
path('cart/', views.cart, name = 'view_cart'),
path('scan/', views.ScanView.as_view(), name='scan'),
path('result/', views.ResultView.as_view(), name='result'),
path('shop/<int:shop_id>/', views.shop_detail, name='shop_detail'),
path('generate_qrcode/', views.generate_qrcode, name='generate_qrcode'),
#user paths
    #home page
path('',views.home,name="home"),
    #user profile
path('profile/',views.profile, name='profile'),
path('update_profile/',views.update_profile, name='update_profile'),
    #scan shops qr code to start shopping
path('scan_store/', views.scanStore, name = 'scanStore'),
    #shopping session starts after scanning
path('start_session/',views.start_session_view, name='start_session'),
    #user scan barcode url
path('user_barcode/', views.userBarcode, name ='userBarcode'),
    #save cart items in the database
path('save_cart/', views.save_cart, name='save_cart'),
    #view cart
path( 'add/', views.add, name='add'),
   # path that checks if a shop exists queried by Ajax
path('check_shop/', views.check_shop, name='check_shop'),
    #path that checks if a product exists queried by Ajax
path('check_prod/', views.check_prod, name='check_prod'),
    #save items in cart session
path('store_cart/', views.store_cart, name='store_cart'),
    # remove item from the cart
path('remove_item/', views.remove_item, name='remove_item'),
    #signout of the current shop
path('shop_signout/',views.shop_signout, name='shop_signout'),
    #check your inventory
path('userInventory/', views.inventory, name='inventory'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)