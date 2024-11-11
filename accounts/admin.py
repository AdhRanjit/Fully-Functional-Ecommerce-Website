#Importing libraries
from django.contrib import admin
from .models import Profile, Cart, CartItem, Order, OrderItem, ShippingAddress

# Register your models here.

admin.site.register(Profile)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(ShippingAddress)
admin.site.register(Order)
admin.site.register(OrderItem)