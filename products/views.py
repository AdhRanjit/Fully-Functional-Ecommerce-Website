from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from products.models import Product, ProductReview, Wishlist
from accounts.models import Cart, CartItem, OrderItem

from .forms import ReviewForm

def get_product(request, slug):
    product = get_object_or_404(Product, slug=slug)
    review = None
    if request.user.is_authenticated:
        try:
            review = ProductReview.objects.get(product=product, user=request.user)
        except ProductReview.DoesNotExist:
            review = None
    
    rating_percentage = 0
    if product.reviews.exists():
        rating_percentage = (product.get_rating() / 5) * 100

    if request.method == 'POST' and request.user.is_authenticated:

        if not OrderItem.objects.filter(order__user=request.user, product_id=product):
            messages.warning(request, "Purchase before reviewing")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if review:
            review_form = ReviewForm(request.POST, instance=review)
        else:
            review_form = ReviewForm(request.POST)

        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Review added successfully!")
            return redirect('get_product', slug=slug)
    else:
        review_form = ReviewForm()
    
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

    context = {
        'product': product,
        'review_form': review_form,
        'rating_percentage': rating_percentage,
        'in_wishlist': in_wishlist,
    }

    return render(request, 'products/product.html', context=context)

@login_required
def add_to_wishlist(request, id):
    product = get_object_or_404(Product, id=id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user, product=product)#, size_variant=size_variant)

    if created:
        messages.success(request, "Product added to Wishlist!")

    return redirect(reverse('wishlist'))

@login_required
def remove_from_wishlist(request, id):
    product = get_object_or_404(Product, id=id)
    size_variant_name = request.GET.get('size')
    
    if size_variant_name:
        Wishlist.objects.filter(user=request.user, product=product).delete()
    else:
        Wishlist.objects.filter(user=request.user, product=product).delete()

    messages.success(request, "Product removed from wishlist!")
    return redirect(reverse('wishlist'))

@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'products/wishlist.html', {'wishlist_items': wishlist_items,})

def move_to_cart(request, id):
    product = get_object_or_404(Product, id=id)

    wishlist = Wishlist.objects.filter(user=request.user, product=product).first()
    
    if not wishlist:
        messages.error(request, "Item not found in wishlist.")
        return redirect('wishlist')

    wishlist.delete()

    cart, created = Cart.objects.get_or_create(user=request.user, is_paid=False)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, "Product moved to cart successfully!")
    return redirect('cart')
