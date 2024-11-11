#Importing libraries
import os
from uuid import uuid4
from django.db import models
from django.conf import settings
from products.models import Product
from django.contrib.auth import get_user_model
from django_countries.fields import CountryField

User = get_user_model()

#Basemodel class to control the system(model)
class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

#Shipping address control
class ShippingAddress(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    street_number = models.CharField(max_length=10)
    zip_code = models.CharField(max_length=30)
    city = models.CharField(max_length=50)
    country = CountryField()
    phone = models.CharField(max_length=30)
    current_address = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.street}, {self.street_number}, {self.city}'

#Profile Control
class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    token = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to='profile', null=True, blank=True)

    def __str__(self):
        return self.user.username

    def get_cart_count(self):
        return CartItem.objects.filter(cart__is_paid=False, cart__user=self.user).count()
    
    def save(self, *args, **kwargs):
        if self.pk:
            try:
                old_profile = Profile.objects.get(pk=self.pk)
                if old_profile.image and old_profile.image != self.image:
                    old_image_path = os.path.join(settings.MEDIA_ROOT, old_profile.image.path)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
            except Profile.DoesNotExist:
                pass

        super(Profile, self).save(*args, **kwargs)

#Cart Control
class Cart(BaseModel):
    is_paid = models.BooleanField(default=False)
    stripe_payment_intent_id = models.CharField(max_length=100, null=True, blank=True)
    stripe_payment_id = models.CharField(max_length=100, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def get_total(self):
        cart_items = self.cartitem_set.all()
        total = 0

        for cart_item in cart_items:
            total += cart_item.get_price()

        return total

#CartItem Control
class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=1)

    def get_price(self):
        price = self.product.price * self.quantity
        return price

#Controlling the order
class Order(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=100, unique=True)
    order_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=100)
    shipping_address = models.TextField(blank=True, null=True)
    payment_mode = models.CharField(max_length=100)
    total = models.DecimalField(max_digits=10, decimal_places=2)

#Controlling the OrderItem
class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    product_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    def get_total_price(self):
        cart_item = CartItem(
            product=self.product,
            quantity=self.quantity
        )
        return cart_item.get_price()