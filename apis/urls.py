from .import views
from django.conf.urls import url
from django.urls import include
from .views import UserViewSet, UserMViewSet, UserAuthViewSet, CategoryViewSet, SubCategoryViewSet, ProductsViewSet
from rest_framework import routers

app_name = "apis"

#API view urls
router = routers.DefaultRouter(trailing_slash=False)
router.register(r'auth', UserAuthViewSet)
router.register(r'users', UserMViewSet,base_name="user")
router.register(r'users/(?P<username>[0-9A-Fa-f\-]+)', UserMViewSet,base_name="user")
router.register(r'categories', CategoryViewSet,base_name='categories')
router.register(r'subcategories', SubCategoryViewSet)
router.register(r'products', ProductsViewSet)