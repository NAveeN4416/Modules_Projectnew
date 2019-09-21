from .import views
from django.conf.urls import url
from django.urls import path, include
from .views import UserViewSet, UserMViewSet, UserAuthViewSet, CategoryViewSet, SubCategoryViewSet, ProductsViewSet
from rest_framework import routers

app_name = "apis"

#API view urls
router = routers.SimpleRouter()
router.register(r'auth', UserAuthViewSet)
router.register(r'users', UserMViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'subcategories', SubCategoryViewSet)
router.register(r'products', ProductsViewSet)