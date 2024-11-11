#Importing Libraries
import json
import stripe
from uuid import uuid4

from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render, get_object_or_404

from products.models import *

from .email_backend import send_account_activation_email
from .models import Profile, Cart, CartItem, ShippingAddress, Order, OrderItem
from .forms import UserUpdateForm, UserProfileForm, ShippingAddressForm, CustomPasswordChangeForm

User = get_user_model()

#handle user login with the help of this function
def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.warning(request, 'Incorrect username or password')
            return HttpResponseRedirect(request.path_info)

        #check whether user's email has been verified or not
        if not user.profile.email_verified:
            messages.error(request, 'Account not verified')
            return HttpResponseRedirect(request.path_info)
        
        #Authenticate the user
        user_obj = authenticate(username=username, password=password)
        
        if user_obj:
            login(request, user_obj) #Login Successful
            messages.success(request, 'Login Successful.')
            return redirect('index')

        messages.warning(request, 'Invalid credentials.')
        
        return HttpResponseRedirect(request.path_info)

    return render(request, 'account/login.html')

##############################################################
##############################################################

#Handling the user signup using signup_page function
def signup_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        pswd = request.POST.get('password')

        #checking if the user name exist or not
        user_obj = User.objects.filter(username=username, email=email)

        if user_obj.exists():
            messages.info(request, 'Username or email already exists!')
            return HttpResponseRedirect(request.path_info)

        #creating an new user and sending activation email
        user_obj = User.objects.create(
            username=username, first_name=fname, last_name=lname, email=email)
        user_obj.set_password(pswd)
        user_obj.save()

        profile = Profile.objects.get(user=user_obj)
        profile.token = str(uuid4())
        profile.save()

        send_account_activation_email(email, profile.token)
        messages.success(request, "An email has been sent to your mail.")
        return HttpResponseRedirect(request.path_info)

    return render(request, 'account/signup.html')

##############################################################
##############################################################

#Logout function
@login_required
def user_logout(request):
    logout(request)
    messages.warning(request, "Logged Out Successfully!")
    return redirect('index')

##############################################################
##############################################################

#activating the user account 
def activate_account(request, token):
    try:
        user = Profile.objects.get(token=token)
        user.email_verified = True
        user.save()
        messages.success(request, 'Account verified')
        return redirect('login')
    except Exception as e:
        return HttpResponse('Invalid token.')

##############################################################
##############################################################

#handling the user cart and handle payment processing
@login_required
def cart(request):
    cart_obj = None
    user = request.user

    try:
        cart_obj = Cart.objects.get(is_paid=False, user=user)

    except Exception as e:
        print(e)
        messages.warning(request, "Your cart is empty. Please sign in or add a product to cart.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    #process the payment
    if cart_obj and request.method=="POST":

        if not ShippingAddress.objects.filter(user=user):
            messages.warning(request, "Your shipping address is empty")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        stripe.api_key = settings.STRIPE_PRIVATE

        ses = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "checkout"
                        },
                        "unit_amount": cart_obj.get_total()*100
                    },
                    "quantity": 1
                }
            ],
            mode="payment",
            success_url=request.build_absolute_uri(reverse("success")) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri(reverse("cart"))
        )
        return JsonResponse({"ses":ses['id']})

    context = {'cart': cart_obj, 'quantity_range': range(1, 6)}
    return render(request, 'account/cart.html', context)

##############################################################
##############################################################

#Adding the products
@login_required
def add_to_cart(request, id):
    try:        
        product = get_object_or_404(Product, id=id)
        cart, _ = Cart.objects.get_or_create(user=request.user, is_paid=False)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        qty = int(request.GET.get('qty', 1))

        if cart_item.quantity+qty>5:
            messages.warning(request, "Cart item cannot exceed 5")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if not created:
            cart_item.quantity += qty
            cart_item.save()
        else:
            if qty>1:
                cart_item.quantity += qty-1
                cart_item.save()

        messages.success(request, 'Item added to cart.')

    except Exception as e:
        print(e)
        messages.error(request, 'Error adding item to cart.')

    return redirect(reverse('cart'))

##############################################################
##############################################################

#Updating the cart item
@require_POST
@login_required
def update_cart_item(request):
    try:
        data = json.loads(request.body)
        cart_item_id = data.get("cart_item_id")
        quantity = int(data.get("quantity"))

        cart_item = CartItem.objects.get(id=cart_item_id, cart__user=request.user, cart__is_paid=False)
        cart_item.quantity = quantity
        cart_item.save()

        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})

##############################################################
##############################################################

#Removing an item from the user cart
@login_required
def remove_cart(request, id):
    try:
        cart_item = get_object_or_404(CartItem, id=id)
        cart_item.delete()
        messages.success(request, 'Item removed from cart.')

    except Exception as e:
        print(e)
        messages.warning(request, 'Error removing item from cart.')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

##############################################################
##############################################################

#Creating an order based on the user's cart
def create_order(cart):
    order, created = Order.objects.get_or_create(
        user=cart.user,
        order_id=cart.stripe_payment_id,
        payment_status="Paid",
        shipping_address=str(ShippingAddress.objects.get(user=cart.user)),
        payment_mode="Card",
        total=cart.get_total(),
    )

    cart_items = CartItem.objects.filter(cart=cart)
    for cart_item in cart_items:
        OrderItem.objects.get_or_create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            product_price=cart_item.get_price()
        )

    return order

##############################################################
##############################################################

#Handling the success page after a successful payment
@login_required
def success(request):
    ses = request.GET.get('session_id')

    stripe.api_key = settings.STRIPE_PRIVATE

    jsn = stripe.checkout.Session.retrieve(ses)

    if jsn['payment_status'] == 'paid':

        send_mail(subject="Order has been placed",
                  message="Hello your order has been placed.",
                  recipient_list=[request.user.email],
                  fail_silently=False,
                  from_email=settings.DEFAULT_FROM_EMAIL)

        cart_obj = Cart.objects.get(is_paid=False, user=request.user)

        cart_obj.is_paid = True
        cart_obj.stripe_payment_intent_id = jsn['payment_intent']
        cart_obj.stripe_payment_id = ses
        cart_obj.save()

        create_order(cart_obj)

    return render(request, 'account/success.html')

##############################################################
##############################################################

#Checking the profile view
@login_required
def profile_view(request, username):
    user_name = get_object_or_404(User, username=username)
    user = request.user
    profile = user.profile

    user_form = UserUpdateForm(instance=user)
    profile_form = UserProfileForm(instance=profile)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    context = {
        'user_name' : user_name,
        'user_form': user_form,
        'profile_form': profile_form
    }

    return render(request, 'account/profile.html', context)

##############################################################
##############################################################

#Changing the password
@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            messages.warning(request, 'Please correct the error below.')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'account/change_password.html', {'form': form})

##############################################################
##############################################################

#Updating the shipping address
@login_required
def update_shipping_address(request):
    shipping_address = ShippingAddress.objects.filter(
        user=request.user, current_address=True).first()
    
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, instance=shipping_address)
        if form.is_valid():
            shipping_address = form.save(commit=False)
            shipping_address.user = request.user
            shipping_address.current_address = True
            shipping_address.save()

            messages.success(request, "The Address Has Been Updated")
            
            form = ShippingAddressForm()
        else:
            form = ShippingAddressForm(request.POST, instance=shipping_address)
    else:
        form = ShippingAddressForm(instance=shipping_address)

    return render(request, 'account/shipping_address.html', {'form': form})

##############################################################
##############################################################

#Checking the history what user ordered
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'account/order_history.html', {'orders': orders})

##############################################################
##############################################################

#Checking the details of the order
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)
    context = {
        'order': order,
        'order_items': order_items,
        'order_total_price': sum(item.get_total_price() for item in order_items),
    }
    return render(request, 'account/order_detail.html', context)