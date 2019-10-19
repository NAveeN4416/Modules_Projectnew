from .import views
from django.conf.urls import url
from django.urls import path, include
from .views import UserViewSet, UserMViewSet, UserAuthViewSet, CategoryViewSet, SubCategoryViewSet, ProductsViewSet
from rest_framework import routers

app_name = "apis"

#API view urls
router = routers.SimpleRouter(trailing_slash=False)
router.register(r'auth', UserAuthViewSet)
router.register(r'users', UserMViewSet,base_name="users")
router.register(r'users/(?P<username>[0-9A-Fa-f\-]+)', UserMViewSet,base_name="users")
router.register(r'categories', CategoryViewSet)
router.register(r'subcategories', SubCategoryViewSet)
router.register(r'products', ProductsViewSet)