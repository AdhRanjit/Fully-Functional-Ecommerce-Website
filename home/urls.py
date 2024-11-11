#Importing path and everything from django.urls and home.views respectively
from django.urls import path
from home.views import *

urlpatterns = [
    path('', index, name="index"),
    path('search/', search, name='search'),
    path('contact/', contact, name='contact'),
    path('about/', about, name='about')
]
