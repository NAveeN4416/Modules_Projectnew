#API View default attrs
    # renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    # parser_classes = api_settings.DEFAULT_PARSER_CLASSES
    # authentication_classes = api_settings.DEFAULT_AUTHENTICATION_CLASSES
    # throttle_classes = api_settings.DEFAULT_THROTTLE_CLASSES
    # permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES
    # content_negotiation_class = api_settings.DEFAULT_CONTENT_NEGOTIATION_CLASS
    # metadata_class = api_settings.DEFAULT_METADATA_CLASS
    # versioning_class = api_settings.DEFAULT_VERSIONING_CLASS


from .Base import BaseView
import os
from log_controller import Initiate_logging
from django.shortcuts import render
from django.contrib.auth.models import User
from users.models import UserDetails
from products.models import Categories, SubCategories, Products, ProductImages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from datetime import datetime
from django.db.models import Q
from django.contrib.auth.hashers import check_password
from apis import constants as C

from rest_framework.decorators import action
from rest_framework.response import Response
from .model_serializers import UserSerializer, UserMSerializer, UserdetailsSerializer, CategorySerializer, SubCategorySerializer, ProductsSerializer
from rest_framework import viewsets
from .CustomViewsets import ThrottledViewSet
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from .CustomAuthentication  import TokenAuthentication as TokenAuth
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.throttling import UserRateThrottle
from .CustomExceptions import CustomThrottled_Exception
from django.conf import settings
import asyncio



class UserAuthViewSet(BaseView,viewsets.ModelViewSet):

	queryset = User.objects.all()
	serializer_class = UserMSerializer


	#===Constructor============================
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)


	@action(detail=False,methods=['post'],url_name="login")
	def login(self,request):

		email    = request.data.get('email',None)
		mobile   = request.data.get('mobile',None)
		password = request.data.get('password',None)

		try:
			user = User.objects.get(Q(username=email) | Q(email=email))
		except User.DoesNotExist as e:
			self.send['message'] = "User not found!"
			return Response(self.send)

		if user :
			check_pass = check_password(password,user.password)

			if check_pass:
				self.send['status']  = 1
				token = Token.objects.get_or_create(user=user)
				self.send['message'] = "Credentials matched"
				self.send['instruction'] = "Use the following `token` in further requests"
				self.send['token']   = str(token[0])
				self.log.info(f"Loggedin || {user}")
			else:
				self.send['message'] = "Password is incorrect"
		else:
			self.send['message'] = "User not found !"

		return Response(self.send)


	@action(detail=False,methods=['get'],url_name="logout")
	def logout(self,request):
		if request.user.is_authenticated:
			user = request.user
			user.auth_token.delete()
			self.log.info(f"LoggedOut || {user} !")
			self.send['status']  = 1
			self.send['message'] = "Logged Out Successfully !"

		return Response(self.send)



class OncePerDayUserThrottle(UserRateThrottle):
        rate = '1/day'


class UserMViewSet(BaseView,ThrottledViewSet):

	queryset          = User.objects.exclude(username='admin')
	serializer_class  = UserMSerializer
	lookup_field      = 'pk'
	multiple_lookup_fields  = ['email','username']

	#authentication_classes = [TokenAuth]
	#permission_classes = [IsAuthenticated,IsAuthenticatedOrReadOnly]
	#renderer_classes 	    = [JSONRenderer,TemplateHTMLRenderer]
	#throttle_classes =  [OncePerDayUserThrottle]
	parser_classes = [MultiPartParser,FileUploadParser]
	throttled_exception_class = CustomThrottled_Exception


	def get_throttled_message(self, request):
		return "request limit exceeded"

	#===Constructor============================
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)


	#Get All Users
	def list(self,request,*args,**kwargs):
		#queryset = get_object_or_404(self.get_queryset(),**request.query_params)
		self.request = request
		users = UserMSerializer(self.get_queryset(),many=True)
		if users.data:
			self.send['data'] = reversed(users.data)
			return self.Send_Response()
		return self.Send_Response(message="Data not found !",status=0)


	#Get Single User
	def retrieve(self,request,pk=0,format='json'):
		try:
			users = self.get_queryset()
			user  = users.get(pk=pk)
			user  = UserMSerializer(user)
		except User.DoesNotExist:
			return self.Send_Response(message='User Not found!',status=0)
		else:
			if user.data:
				self.send['data']  = user.data
				return self.Send_Response()

	#Create user
	def create(self,request):
		message = "Invalid data submitted !"

		#Details Table Serialization & Validation
		status, details_serializer = self.Serialize_Method(UserdetailsSerializer,request.data)
		if not status:
			self.required_fields(details_serializer)
			return self.Send_Response(message=message,status=0)

		data = request.data.copy()
		existance_flag = User.objects.filter(email=data.get('email',None))

		#Check for user existance
		if not existance_flag:
			data.update({'date_joined':datetime.now()})

			#Users Table Serialization & Validation
			status, serializer = self.Serialize_Method(UserMSerializer,data)
			if status:
				#Saving both tables data one/one
				user_instance = serializer.save()
				details_instance = details_serializer.save(user=user_instance)
				self.log.info(f"{request.user} created {user_instance} - {user_instance.pk}!")
				message = C.USERCREATED; status = 1
			else:
				self.required_fields(serializer)
				status = 0
		else:
			message = C.USERALREADYEXIST; status = 0

		return self.Send_Response(message=message,status=status)


	#Update User
	def update(self,request,pk=0,format='json'):
		self.log.info(f"{request.user} || Record-{pk} || Updated!")
		return self.Send_Response(message = 'Update Checking !')


	#Partial Update User
	def partial_update(self, request, pk=0,format='json'):
		user_instance = details_instance = None

		try:
			users = self.get_queryset()
			user  = users.get(pk=pk)
		except User.DoesNotExist:
			return self.Send_Response(message='User Not found!',status=0)
		else:
			status, serializer = self.Serialize_Method(UserMSerializer,request.data,instance=user,partial=True)
			if status:
				user_instance = serializer.save()
			else:
				user_instance = user
				self.required_fields(serializer) #Append serializer errors to response
				return self.Send_Response(message="Bad Request",status=0)

			#if user found update userdetails in data presence
			user_details = UserDetails.objects.filter(user=user)
			if user_details:
				user_details = user_details[0]

				status, details_serializer = self.Serialize_Method(UserdetailsSerializer,request.data,instance=user_details,partial=True)
				if status:
					details_instance = details_serializer.save()
				else:
					self.required_fields(details_serializer) #Append serializer errors to response
					return self.Send_Response(message="Bad Request",status=0)

			if user_instance or details_serializer:
				message = f"{user_instance} updated Successfully :)"
				self.log.info(f"{request.user} updated {user} - {user.pk}!")
				return self.Send_Response(message=message)

		return self.Send_Response(message="Details not found !",status=0)


	#Delete User
	def destroy(self,request,pk=0,format='json'):
		try:
			users = self.get_queryset()
			user  = users.get(pk=pk)
			user.delete()
			self.log.info(f"{request.user} deleted {user} - {pk}!")
			return self.Send_Response(message=f"{user} was deleted Successfully :)")
		except User.DoesNotExist:
			return self.Send_Response(message='User Not found!',status=0)


	#Change user status
	@action(detail=True, methods=['get'], url_name="useractivity")
	def useractivity(self,request,pk=0,format='json'):
		try:
			user = User.objects.get(pk=pk)
		except User.DoesNotExist:
			message = "User not found !"; status = '0'
		else:
			user.is_active = False if user.is_active else True
			user.save()
			message = C.ACTIVATED if user.is_active else C.DEACTIVATED; status = '1'

		return self.Send_Response(message=message,status=status)




	def filter_queryset(self,queryset,filter_fields):
		query = Q()

		for field, value in filter_fields.items():
			query |= Q(f"{field}={value}")
		return queryset.filter(query)


	def get_permissions(self):
	 	permission_classes = []
	 	if self.action in ['create','update','partial_update','destroy']:
	 		permission_classes = [IsAuthenticated]

	 	return [permission() for permission in permission_classes]


	def get_queryset(self):
		queryset = User.objects.exclude(username='admin')

		query_params = self.request.query_params
		filter_fields = {}
		for field in self.multiple_lookup_fields:
			if query_params.get(field):
				filter_fields[field] = query_params.get(field)
		print(filter_fields)
		if filter_fields:
			queryset = queryset.filter(**filter_fields)

		return queryset



#------------------------------------- Category View Set -------------------------------------------

class CategoryViewSet(BaseView,viewsets.ModelViewSet):

	queryset         	   = Categories.objects.filter(status=1)
	serializer_class 	   = CategorySerializer

	authentication_classes = [TokenAuth]
	#permission_classes     = [IsAuthenticated]
	#renderer_classes 	    = [JSONRenderer,TemplateHTMLRenderer]

	#===Constructor=====================
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)


	def list(self,request,format="json"):
		category_serializer = CategorySerializer(self.queryset,many=True)

		self.send['data'] = category_serializer.data

		if self.send['data']:
			self.send['status']  = 1
			self.send['message'] = "Success" 

		return Response(self.send)
		#return Response(request.META)


	def retrieve(self,request,pk=0):
		category = Categories.objects.filter(pk=pk)

		if category and category[0]:
			category_serializer = CategorySerializer(instance=category[0])
			self.send['data'] = category_serializer.data

		if self.send['data']:
			self.send['status']  = 1 
			self.send['message'] = "Success"

		return Response(self.send)


	@action(detail=True,methods=['get'],url_name="getsubcategories")
	def subcategories(self,request,pk=0):
		try:
			category = self.queryset.get(pk=pk)
		except Categories.DoesNotExist:
			return Response(self.send)

		subcategories = SubCategories.objects.filter(category=category)
		subcategory_serializer = SubCategorySerializer(subcategories,many=True)

		self.send['data'] = subcategory_serializer.data

		if self.send['data']:
			self.send['status']  = 1 
			self.send['message'] = "Success" 

		return Response(self.send)


	@action(detail=True,methods=['get'],url_name="getproducts")
	def products(self,request,pk=0):
		try:
			category = self.queryset.get(pk=pk)
		except Categories.DoesNotExist:
			return Response(self.send)

		subcategories = SubCategories.objects.filter(category=category)
		data = []
		for subcategory in subcategories:
			products = Products.objects.filter(subcategory=subcategory).filter(status=1)
			product_serializer = ProductsSerializer(products,many=True)
			for product in product_serializer.data:
				data.append(product)

		self.send['data'] = data

		if data:
			self.send['status']  = 1 
			self.send['message'] = "Success"

		return Response(self.send)


	def create(self,request):
		self.send['message'] = "Sorry, Not Implemented"
		return Response(self.send)

	def update(self,request,pk=None):
		self.send['message'] = "Sorry, Not Implemented"
		return Response(self.send)

	def partial_update(self,request,pk=None):
		self.send['message'] = "Sorry, Not Implemented"
		return Response(self.send)

	def destroy(self,request,pk=None):
		self.send['message'] = "Sorry, Not Implemented"
		return Response(self.send)


class ReadCategoryViewSet(BaseView,viewsets.ReadOnlyModelViewSet):

	queryset         	   = Categories.objects.filter(status=1)
	serializer_class 	   = CategorySerializer

	#authentication_classes = [TokenAuth]
	#permission_classes     = [IsAuthenticated]
	#renderer_classes 	    = [JSONRenderer,TemplateHTMLRenderer]


	#===Constructor=====================
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)


	def list(self,request,format="json"):
		category_serializer = CategorySerializer(self.queryset,many=True)

		self.send['data'] = category_serializer.data

		if self.send['data']:
			self.send['status']  = 1 
			self.send['message'] = "Success" 

		return Response(self.send)


	def retrieve(self,request,pk=0):
		category = Categories.objects.filter(pk=pk)

		if category and category[0]:
			category_serializer = CategorySerializer(instance=category[0])
			self.send['data'] = category_serializer.data

		if self.send['data']:
			self.send['status']  = 1
			self.send['message'] = "Success"

		return Response(self.send)


	@action(detail=True,methods=['get'],url_name="getsubcategories")
	def subcategories(self,request,pk=0):
		try:
			category = self.queryset.get(pk=pk)
		except Categories.DoesNotExist:
			return Response(self.send)

		subcategories = SubCategories.objects.filter(category=category)
		subcategory_serializer = SubCategorySerializer(subcategories,many=True)

		self.send['data'] = subcategory_serializer.data

		if self.send['data']:
			self.send['status']  = 1
			self.send['message'] = "Success" 

		return Response(self.send)

	@action(detail=True,methods=['get'],url_name="getproducts")
	def products(self,request,pk=0):
		try:
			category = self.queryset.get(pk=pk)
		except Categories.DoesNotExist:
			return Response(self.send)

		subcategories = SubCategories.objects.filter(category=category)
		data = []
		for subcategory in subcategories:
			products = Products.objects.filter(subcategory=subcategory).filter(status=1)
			product_serializer = ProductsSerializer(products,many=True)
			for product in product_serializer.data:
				data.append(product)

		self.send['data'] = data

		if data:
			self.send['status']  = 1
			self.send['message'] = "Success"

		return Response(self.send)

#-------------------------------------Sub Categgory View Set -------------------------------------------

class SubCategoryViewSet(BaseView,viewsets.ModelViewSet):

	queryset         	   = SubCategories.objects.filter(status=1)
	serializer_class 	   = SubCategorySerializer

	authentication_classes = [TokenAuth]
	#permission_classes     = [IsAuthenticated]
	#renderer_classes 	    = [JSONRenderer,TemplateHTMLRenderer]

	#===Constructor=====================
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)


	def list(self,request):

		subcategory_serializer = SubCategorySerializer(self.queryset,many=True)

		self.send['data'] = subcategory_serializer.data

		if self.send['data']:
			self.send['status']  = 1 
			self.send['message'] = "Success" 

		return Response(self.send)


	def retrieve(self,request,pk=0):
		subcategory = SubCategories.objects.filter(pk=pk)

		if subcategory and subcategory[0]:
			subcategory_serializer = SubCategorySerializer(subcategory[0])
			self.send['data'] = subcategory_serializer.data

		if self.send['data']:
			self.send['status']  = 1 
			self.send['message'] = "Success" 

		return Response(self.send)


	@action(detail=True,methods=['get'],url_name="getproducts")
	def products(self,request,pk=0):
		subcategory = self.queryset.get(pk=pk)
		products = Products.objects.filter(subcategory=subcategory)
		product_serializer = ProductsSerializer(products,many=True)

		self.send['data'] = product_serializer.data

		if self.send['data']:
			self.send['status']  = 1 
			self.send['message'] = "Success" 

		return Response(self.send)


	def create(self,request):
		self.send['message'] = "Not Implemented"
		return Response(self.send)

	def update(self,request,pk=None):
		self.send['message'] = "Not Implemented"
		return Response(self.send)

	def partial_update(self,request,pk=None):
		self.send['message'] = "Not Implemented"
		return Response(self.send)

	def destroy(self,request,pk=None):
		self.send['message'] = "Not Implemented"
		return Response(self.send)

#------------------------------------- Products View Set -------------------------------------------

class ProductsViewSet(BaseView,viewsets.ModelViewSet):

	queryset         	   = Products.objects.filter(status=1)
	serializer_class 	   = ProductsSerializer

	authentication_classes = [TokenAuth]
	#permission_classes     = [IsAuthenticated]
	#renderer_classes 	    = [JSONRenderer,TemplateHTMLRenderer]


	#===Constructor=====================
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)


	def list(self,request):

		product_serializer = ProductsSerializer(self.queryset,many=True)

		self.send['data'] = product_serializer.data

		if self.send['data']:
			self.send['status']  = 1 
			self.send['message'] = "Success" 

		return Response(self.send)


	def retrieve(self,request,pk=0):
		product = Products.objects.filter(pk=pk)

		if product and product[0]:
			product_serializer = ProductsSerializer(product[0])
			self.send['data'] = product_serializer.data

		if self.send['data']:
			self.send['status']  = 1
			self.send['message'] = "Success"

		return Response(self.send)


	def create(self,request):
		self.send['message'] = "Not Implemented"
		return Response(self.send)

	def update(self,request,pk=None):
		self.send['message'] = "Not Implemented"
		return Response(self.send)

	def partial_update(self,request,pk=None):
		self.send['message'] = "Not Implemented"
		return Response(self.send)

	def destroy(self,request,pk=None):
		self.send['message'] = "Not Implemented"
		return Response(self.send)



# ViewSets define the view behavior.
class UserViewSet(viewsets.ViewSet):

	queryset         = User.objects.all()
	serializer_class = UserSerializer

	def list(self,request):
		queryset = User.objects.all()
		serializer = UserSerializer(queryset,many=True)
		return Response(serializer.data)

	def retrieve(self,request,pk=0):
		queryset = User.objects.all()
		queryset = get_object_or_404(queryset,pk=pk)
		serializer = UserSerializer(queryset)
		return Response(serializer.data)




from rest_framework.decorators import api_view

results = 0





@api_view(['GET', 'POST'])
def Purchase_product(request):

	async def check_asyncio():
		global results
		results = 10
		await asyncio.sleep(10)

	async def main():
		task = asyncio.create_task(check_asyncio())
		await task

	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	loop = asyncio.get_event_loop()
	t = loop.run_until_complete(main())
	return Response({"message": results})

	#import requests
	#import json
	#from io import BytesIO


	#headers 	= {'Authorization' : 'Token 0cd82f85409da40ab4bb2e3868162909deb1fedd'}
	#credentials = {'email': 'anil@yopmail.com', 'password': 'Kaki@1234'}


	# kwargs = {
	# 			'get' 	  		  : 'params',
	# 			'post'	  		  : 'data',
	# 			'headers' 		  : 'headers',
	# 			'auth'    		  : 'auth',
	# 			'cookies' 		  : 'cookies',
	# 			'json'    		  : 'json',
	# 			'files'   		  : 'files',
	# 			'allow_redirects' : 'True/False',
	# 			'timeout'         : '0.01',
	# 		 }


	#response = requests.post('http://localhost:8000/apis/auth/user_login',data=credentials,headers=headers,timeout=0.01)



