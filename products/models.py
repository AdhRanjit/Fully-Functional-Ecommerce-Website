from uuid import uuid4
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User

# Create your models here.

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class Category(BaseModel):
    category_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
   
    def save(self, *args, **kwargs):
        self.slug = slugify(self.category_name)
        super(Category, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.category_name

class Product(BaseModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.IntegerField()
    description = models.TextField()
    newest = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

    def get_rating(self):
        total = sum(int(review['stars']) for review in self.reviews.values())

        if self.reviews.count() > 0:
            return total / self.reviews.count()
        else:
            return 0


class ProductImage(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product')


class ProductReview(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    stars = models.IntegerField(default=3, choices=[(i, i) for i in range(1, 6)])
    content = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)


class Wishlist(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlisted_by")
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self) -> str:
        return f'{self.user.username} - {self.product.product_name}'

    
