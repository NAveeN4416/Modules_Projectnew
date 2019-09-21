from django.contrib import admin

# Register your models here.
from .models import Categories, SubCategories, Products, ProductImages

admin.site.register(Categories)
admin.site.register(SubCategories)
admin.site.register(Products)
admin.site.register(ProductImages)