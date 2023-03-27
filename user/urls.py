from django.urls import path
from . import views
from .views import logout_view

urlpatterns = [
path('',views.home,name="home"),
path('signin/',views.signin, name='signin'),
path('signup/',views.signup, name='signup'),
path('profile/',views.profile, name='profile'),
path('add/',views.cart, name='add_cart'),
path( 'dashboard/', views.dashboard, name='dashboard'),
path('cartdash/', views.cartdash, name = 'cartdash'),
path('cart/', views.cart, name = 'view_cart'),
path( 'add/', views.add, name='add'),
# path('barcode/', views.generate_barcode, name='barcode_scanner')
path('scan/', views.ScanView.as_view(), name='scan'),
path('result/', views.ResultView.as_view(), name='result'),
path('user_barcode/', views.userBarcode, name ='userBarcode'),
path('shop_product/', views.shopProduct, name='shopProduct'),
path('payment_validation/', views.paymentVal, name='paymentVal'),
path('scan_store/', views.scanStore, name = 'scanStore'),
path('logout/', logout_view, name='logout'),
]