from django.urls import path
from . import views
from .views import logout_view
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
path('',views.home,name="home"),
path('home2/',views.admin_home, name="admin_home"),
path('signin/',views.signin, name='signin'),
path('signup/',views.signup, name='signup'),
path('profile/',views.profile, name='profile'),
# path('add/',views.cart, name='add_cart'),
path( 'dashboard/', views.dashboard, name='dashboard'),
path('cartdash/', views.cartdash, name = 'cartdash'),
path('cart/', views.cart, name = 'view_cart'),
path( 'add/', views.add, name='add'),
path('barcode/', views.generate_barcode, name='barcode_scanner'),
path('scan/', views.ScanView.as_view(), name='scan'),
path('result/', views.ResultView.as_view(), name='result'),
path('user_barcode/', views.userBarcode, name ='userBarcode'),
path('shop_product/', views.shopProduct, name='shopProduct'),
path('payment_validation/', views.paymentVal, name='paymentVal'),
path('scan_store/', views.scanStore, name = 'scanStore'),
 path('start_session/',views.start_session_view, name='start_session'),
path('logout/', logout_view, name='logout'),
path('store_cart/', views.store_cart, name='store_cart'),
# remove cart item
path('remove_item/', views.remove_item, name='remove_item'),
path('shop_signout/',views.shop_signout, name='shop_signout'),
 # path for the AJAX view that checks if a shop exists
path('check_shop/', views.check_shop, name='check_shop'),
path('check_prod/', views.check_prod, name='check_prod'),
path('addshop/', views.add_shop, name='add_shop'),
path('shop/<int:shop_id>/', views.shop_detail, name='shop_detail'),
path('generate_qrcode/', views.generate_qrcode, name='generate_qrcode'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)