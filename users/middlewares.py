from django.conf import settings
from django.contrib import auth
from django.contrib.auth import load_backend
from django.contrib.auth.backends import RemoteUserBackend
from django.core.exceptions import ImproperlyConfigured
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject
from django.conf import settings


class Set_RequestObject(MiddlewareMixin):

    def process_request(self,request):
    	#print(request.content_type)
    	settings.REQUEST_OBJECT = request
    	request.CONTENT_TYPE    = request.META.get('CONTENT_TYPE')


    def process_response(self,request,response):
    	#print(response.data)
    	return response