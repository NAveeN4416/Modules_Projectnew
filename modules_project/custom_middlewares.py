# from django.conf import settings
# from django.contrib import auth
# from django.contrib.auth import load_backend
# from django.contrib.auth.backends import RemoteUserBackend
# from django.core.exceptions import ImproperlyConfigured
from django.utils.deprecation import MiddlewareMixin
# from django.utils.functional import SimpleLazyObject
from django.conf import settings



class Set_RequestObject(MiddlewareMixin):

	def process_request(self,request):
		settings.REQUEST_OBJECT = request