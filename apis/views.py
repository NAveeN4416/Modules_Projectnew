#API View default attrs
    # renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    # parser_classes = api_settings.DEFAULT_PARSER_CLASSES
    # authentication_classes = api_settings.DEFAULT_AUTHENTICATION_CLASSES
    # throttle_classes = api_settings.DEFAULT_THROTTLE_CLASSES
    # permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES
    # content_negotiation_class = api_settings.DEFAULT_CONTENT_NEGOTIATION_CLASS
    # metadata_class = api_settings.DEFAULT_METADATA_CLASS
    # versioning_class = api_settings.DEFAULT_VERSIONING_CLASS


from log_controller import Initiate_logging
import os
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
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from .CustomAuthentication  import TokenAuthentication as TokenAuth
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FileUploadParser, MultiPartParser
from django.conf import settings


#Create a log path for this file
file_name = __name__.split('.')
file_path = '/'.join(file_name)
log_path  = f"logs/{file_path}/"
os.makedirs(log_path,exist_ok=True)


def login_required():

	send = {}
	send['status']  = '0'
	send['message'] = "Please login !"
	send['data']    = {}

	return Response(send)


def Serialize_Method(SerializerClass,data,instance=None,many=False,partial=False):

	if instance:
		details_serializer = SerializerClass(instance,data=data,many=many,partial=partial)
	else:
		details_serializer = SerializerClass(data=data,many=many)

	if details_serializer.is_valid():#Check opposite
		return (True, details_serializer)
	return (False, details_serializer)



def required_fields(self,serializer):
	validation_rules = {}
	errors = {}

	for key, value in  serializer.fields.items():
		validation_rules[key] = value.error_messages

	for key, value in serializer.errors.items():
		errors[key] = value[0]

	self.send['errors'] = errors
	#self.send['validation_rules'] = validation_rules


class UserAuthViewSet(viewsets.ModelViewSet):

	queryset = User.objects.all()
	serializer_class = UserMSerializer
	#authentication_classes = [TokenAuth]

	#Tracking User Authentication
	report_name = f"{log_path}/Authentication"
	Log = Initiate_logging(report_name,10)
	authlog = Log.Track()


	#===Constructor============================
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.send    = {}
		self.send['status']  = '0'
		self.send['message'] = "User Not found!"



	@action(detail=False,methods=['post'],url_name="user_login")
	def user_login(self,request):

		email    = request.POST.get('email',None)
		mobile   = request.POST.get('mobile',None)
		password = request.POST.get('password',None)

		user = User.objects.get(Q(username=email) | Q(email=email))
		if user :
			check_pass = check_password(password,user.password)

			if check_pass:
				self.send['status']  = '1'
				token = Token.objects.get_or_create(user=user)
				self.send['message'] = "Loggedin Success"
				self.send['token']   = str(token[0])
				self.authlog.info(f"Loggedin || {user}")
			else:
				self.send['message'] = "Password is incorrect"
		else:
			self.send['message'] = "User not found !"

		return Response(self.send)


	@action(detail=False,methods=['get'],url_name="user_logout")
	def user_logout(self,request):
		if request.user.is_authenticated:
			user = request.user
			request.user.auth_token.delete()
			self.authlog.info(f"LoggedOut || {user} !")
			self.send['status']  = '1'
			self.send['message'] = "Logged Out Successfully !"

		return Response(self.send)


class UserMViewSet(viewsets.ModelViewSet):

	#queryset          = User.objects.all()
	serializer_class  = UserMSerializer
	lookip_field      = 'username'
	#multiple_lookup_fields  = ['username','email']

	authentication_classes = [TokenAuth]
	#permission_classes     = [IsAuthenticated]
	#renderer_classes 	    = [JSONRenderer,TemplateHTMLRenderer]
	parser_classes = [MultiPartParser,FileUploadParser]


	#Tracking User Authentication
	report_name = f"{log_path}/UserModel"
	Log = Initiate_logging(report_name,10)
	tracking_user = Log.Track()

	#===Constructor============================
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.send    = {}
		self.details = {}
		self.request = None

		#Default
		self.send['status']  = '0'
		self.send['message'] = "User Not found!"
		self.send['data']    = {}


	def get_queryset(self):
		return User.objects.exclude(username='admin')


	#Get All Users
	def list(self,request,*args,**kwargs):
		users = UserMSerializer(self.get_queryset(),many=True)

		if users.data:
			self.send['data'] = reversed(users.data)
			return self.Send_Response()

		return self.Send_Response(message="Data not found !",status=0)


	#Get Single User
	def retrieve(self,request,pk=0):
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
		status, details_serializer = Serialize_Method(UserdetailsSerializer,request.data)
		if not status:
			required_fields(self,details_serializer)
			return self.Send_Response(message=message,status=0)

		data = request.POST.copy()
		existance_flag = User.objects.filter(email=data.get('email',None))

		#Check for user existance
		if not existance_flag:
			data.update({'date_joined':datetime.now()})

			#Users Table Serialization & Validation
			status, serializer = Serialize_Method(UserMSerializer,data)
			if status:
				#Saving both tables data one/one
				user_instance = serializer.save()
				details_instance = details_serializer.save(user=user_instance)
				self.tracking_user.info(f"{request.user} created {user_instance} - {user_instance.pk}!")
				message = C.USERCREATED; status = 1
			else:
				required_fields(self,serializer)
				status = 0
		else:
			message = C.USERALREADYEXIST; status = 0

		return self.Send_Response(message=message,status=status)


	#Update User
	def update(self,request,pk=0):
		self.tracking_user.info(f"{request.user} || Record-{pk} || Updated!")
		return self.Send_Response(message = 'Update Checking !')


	#Partial Update User
	def partial_update(self, request, pk=0):
		user_instance = details_instance = None

		try:
			users = self.get_queryset()
			user  = users.get(pk=pk)
		except User.DoesNotExist:
			return self.Send_Response(message='User Not found!',status=0)
		else:
			status, serializer = Serialize_Method(UserMSerializer,request.data,instance=user,partial=True)
			if status:
				user_instance = serializer.save()

			#if user found update userdetails in data presence
			user_details = UserDetails.objects.filter(user=user)
			if user_details:
				user_details = user_details[0]

				status, details_serializer = Serialize_Method(UserdetailsSerializer,request.data,instance=user_details,partial=True)
				if status:
					details_instance = details_serializer.save()

			if user_instance or details_serializer:
				message = f"{user_instance} updated Successfully :)"
				self.tracking_user.info(f"{request.user} updated {user} - {user.pk}!")
				return self.Send_Response(message=message)

		return self.Send_Response(message="Details not found !",status=0)


	#Delete User
	def destroy(self,request,pk=0):
		try:
			users = self.get_queryset()
			user  = users.get(pk=pk)
			user.delete()
			self.tracking_user.info(f"{request.user} deleted {user} - {pk}!")
			return self.Send_Response(message=f"{user} was deleted Successfully :)")
		except User.DoesNotExist:
			return self.Send_Response(message='User Not found!',status=0)


	#Change users status
	@action(detail=True,methods=['get'], url_name="useractivity")
	def useractivity(self,request,pk=0):
		try:
			user = User.objects.get(pk=pk)
		except User.DoesNotExist:
			message = "User not found !"; status = '0'
		else:
			user.is_active = False if user.is_active else True
			user.save()
			message = C.ACTIVATED if user.is_active else C.DEACTIVATED; status = '1'

		return self.Send_Response(message=message,status=status)


	#////////////////Helping Methods///////////////
	def Send_Response(self,message='Success',status=1):
		self.send['status']  = status
		self.send['message'] = message

		return Response(self.send)

#------------------------------------- Categgory View Set -------------------------------------------

class CategoryViewSet(viewsets.ModelViewSet):

	queryset         	   = Categories.objects.filter(status=1)
	serializer_class 	   = CategorySerializer

	authentication_classes = [TokenAuth]
	#permission_classes     = [IsAuthenticated]
	#renderer_classes 	    = [JSONRenderer,TemplateHTMLRenderer]


	#Tracking User Authentication
	report_name = f"{log_path}/CategoryModel"
	Log = Initiate_logging(report_name,10)
	product_log = Log.Track()


	#===Constructor=====================
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.send    = {}
		self.details = {}
		self.request = None
		self.single_record  = False

		self.send['status']  = '0'
		self.send['message'] = "Data Not found!"
		self.send['data']    = {}


	def list(self,request,format="json"):

		category_serializer = CategorySerializer(self.queryset,many=True)

		self.send['data'] = category_serializer.data

		if self.send['data']:
			self.send['status']  = '1' 
			self.send['message'] = "Success" 

		return Response(self.send)


	def retrieve(self,request,pk=0):

		if request.auth is None:
			return login_required()

		category = Categories.objects.filter(pk=pk)

		if category and category[0]:
			category_serializer = CategorySerializer(instance=category[0])
			self.send['data'] = category_serializer.data

		if self.send['data']:
			self.send['status']  = '1' 
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
#-------------------------------------Sub Categgory View Set -------------------------------------------

class SubCategoryViewSet(viewsets.ModelViewSet):

	queryset         	   = SubCategories.objects.filter(status=1)
	serializer_class 	   = SubCategorySerializer

	authentication_classes = [TokenAuth]
	#permission_classes     = [IsAuthenticated]
	#renderer_classes 	    = [JSONRenderer,TemplateHTMLRenderer]


	#Tracking User Authentication
	report_name = f"{log_path}/CategoryModel"
	Log = Initiate_logging(report_name,10)
	product_log = Log.Track()


	#===Constructor=====================
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.send    = {}
		self.details = {}
		self.request = None
		self.single_record  = False

		self.send['status']  = 0
		self.send['message'] = "Data Not found!"
		self.send['data']    = {}


	def list(self,request):

		subcategory_serializer = SubCategorySerializer(self.queryset,many=True)

		self.send['data'] = subcategory_serializer.data

		if self.send['data']:
			self.send['status']  = '1' 
			self.send['message'] = "Success" 

		return Response(self.send)


	def retrieve(self,request,pk=0):
		subcategory = SubCategories.objects.filter(pk=pk)

		if subcategory and subcategory[0]:
			subcategory_serializer = SubCategorySerializer(subcategory[0])
			self.send['data'] = subcategory_serializer.data

		if self.send['data']:
			self.send['status']  = '1' 
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

class ProductsViewSet(viewsets.ModelViewSet):

	queryset         	   = Products.objects.filter(status=1)
	serializer_class 	   = ProductsSerializer

	authentication_classes = [TokenAuth]
	#permission_classes     = [IsAuthenticated]
	#renderer_classes 	    = [JSONRenderer,TemplateHTMLRenderer]


	#Tracking User Authentication
	report_name = f"{log_path}/ProductModel"
	Log = Initiate_logging(report_name,10)
	product_log = Log.Track()


	#===Constructor=====================
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.send    = {}
		self.details = {}
		self.request = None
		self.single_record  = False

		self.send['status']  = '0'
		self.send['message'] = "Data Not found!"
		self.send['data']    = {}


	def list(self,request):

		product_serializer = ProductsSerializer(self.queryset,many=True)

		self.send['data'] = product_serializer.data

		if self.send['data']:
			self.send['status']  = '1' 
			self.send['message'] = "Success" 

		return Response(self.send)


	def retrieve(self,request,pk=0):
		product = Products.objects.filter(pk=pk)

		if product and product[0]:
			product_serializer = ProductsSerializer(product[0])
			self.send['data'] = product_serializer.data

		if self.send['data']:
			self.send['status']  = '1'
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
