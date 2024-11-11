#Importing AppConfig library from django.apps
from django.apps import AppConfig

# HomeConfig class for further processing
class HomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'home'
