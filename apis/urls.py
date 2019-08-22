from .import views
from django.conf.urls import url
from django.urls import path, include
from .views import UserViewSet, UserMViewSet, UserAuthViewSet
from rest_framework import routers

app_name = "apis"

#API view urls
router = routers.DefaultRouter()
router.register(r'users', UserMViewSet)
router.register(r'auth', UserAuthViewSet)