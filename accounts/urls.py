#Importing libraries
from .views import *
from django.urls import path
from django.contrib.auth import views 

#Controlling the path for all pages of the website
urlpatterns = [
    path('login/', login_page, name="login"),
    path('signup/', signup_page, name="signup"),
    path('logout/', user_logout, name='logout'),
    path('activate/<token>/', activate_account, name="activate-account"),

    path('cart/', cart, name="cart"),
    path('add-to-cart/<id>/', add_to_cart, name="add_to_cart"),
    path('update_cart_item/', update_cart_item, name='update_cart_item'),
    path('remove-cart/<id>/', remove_cart, name="remove_cart"),
    path('success', success, name="success"),
    
    path('profile/<str:username>/', profile_view, name='profile'),
    path('change-password/', change_password, name='change_password'),
    path('shipping-address/', update_shipping_address, name='shipping-address'),
    
    path('password_reset/', views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    

    path('order-history/', order_history, name='order_history'),
    path('order-details/<str:order_id>/', order_detail, name='order_detail'),
]
