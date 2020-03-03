from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.http import HttpResponse


class Set_RequestObject(MiddlewareMixin):

    def process_request(self,request):
        #return HttpResponse("asdfas")
    	#print(request.content_type)
    	settings.REQUEST_OBJECT = request
    	request.CONTENT_TYPE    = request.META.get('CONTENT_TYPE')
        


    def process_response(self,request,response):
    	#print(response.data)
    	return response