#Importing libraries
from django.db.models import Q
from django.conf import settings
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.validators import validate_email

from products.models import Product, Category

#fetching all the products and categories and retrieving it
def index(request):
    pdts = Product.objects.all()
    cats = Category.objects.all()
    srt = request.GET.get('sort')
    s_cat = request.GET.get('category')

    #filtering products by selected category
    if s_cat:
        pdts = pdts.filter(category__category_name=s_cat)

    #sorting products by selected category from above code
    if srt:
        if srt == 'newest':
            pdts = pdts.filter(newest=True).order_by('category_id')

        elif srt == 'priceAsc':
            pdts = pdts.order_by('price')

        elif srt == 'priceDesc':
            pdts = pdts.order_by('-price')

    #Preparing contect data for rendering the template
    context = {
        'products': pdts,
        'categories': cats,
        'selected_category': s_cat,
        'selected_sort': srt,
    }

    #returning the index page with the context data
    return render(request, 'home/index.html', context)

#Get the search query from GET Parameters
def search(request):
    query = request.GET.get('q', '')
    if query:
        pdts = Product.objects.filter(Q(name__icontains=query) | Q(name__istartswith=query))
    else:
        pdts = Product.objects.none()

    context = {'query': query, 'products': pdts}
    return render(request, 'home/search.html', context)

#Checking whether the request method is POST or not
def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        message = request.POST.get('message')
        try:
            validate_email(email)
        except:
            messages.error(request, 'Invalid Email')

        messages.success(request, 'Thank you for your message. We will get back to you soon..')
        return HttpResponseRedirect(request.path_info)
    
    return render(request, 'home/contact.html')

#Rendering the about page
def about(request):
    return render(request, 'home/about.html')
