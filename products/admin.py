from django.contrib import admin
from .models import ProductImage, Category, Product, ProductReview

admin.site.register(Category)

class ProductImageAdmin(admin.StackedInline):
    model = ProductImage

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']
    inlines = [ProductImageAdmin]

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(ProductReview)