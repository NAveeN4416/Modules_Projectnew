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


class UserAuthViewSet(viewsets.ModelViewSet):

	queryset = User.objects.all()
	serializer_class = UserMSerializer
	authentication_classes = [TokenAuth]

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
	#lookip_field      = 'pk'
	multiple_lookup_fields  = ['username','email']

	authentication_classes = [TokenAuth]
	#permission_classes     = [IsAuthenticated]
	#renderer_classes 	    = [JSONRenderer,TemplateHTMLRenderer]


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

		self.send['status']  = '0'
		self.send['message'] = "User Not found!"
		self.send['data']    = {}

	
	def get_object(self):
	    queryset = self.get_queryset()
	    filter = {}
	    for field in self.kwargs:
	        filter[field] = self.kwargs[field]

	    obj = get_object_or_404(queryset, **filter)
	    self.check_object_permissions(self.request, obj)
	    return obj


	def get_queryset(self):
		return User.objects.all()

	#==Inherited Methods (Request Recievers)==
	#Get All Users
	def list(self,request,*args,**kwargs):

		users = UserMSerializer(self.get_queryset(),many=True)

		if self.ProcessUsers(users):
			users = self.userslist
			self.send['status']  = '1'
			self.send['message'] = "success"
			self.send['data']    = users
			return Response(self.send)

		self.send['message'] = "Data not found !"

		return Response(self.send)


	def ProcessUsers(self,users):

		if users.data:
			self.userslist = users.data
			return True
		return False


	#Get Single User
	def retrieve(self,request,pk=0):
		try:
			users = User.objects.get(pk=pk)
			users = UserMSerializer(users)
		except User.DoesNotExist:
			pass
		else:
			if self.ProcessUsers(users):
				self.send['status']  = '1'
				self.send['message'] = "success"
				self.send['data']    = self.userslist

		return Response(self.send)


	#Delete User
	def destroy(self,request,pk=0):
		self.tracking_user.info(f"{request.user} || Record-{pk} || Deleted!")
		return Response({'message':"You are trying to delete record id {}".format(pk)})


	#Create user
	def create(self,request):
		data = request.POST.copy()
		data.update({'date_joined':datetime.now()})

		serializer = UserSerializer(data=data)

		users = User.objects.filter(Q(username=data['username']) | Q(email=data['email']))

		if not users:
			serializer = UserSerializer(data=data)
			if serializer.is_valid():
				instance = UserSerializer(serializer,data=data)
				serializer.save()
				self.send['status']  = "1"
				self.send['message'] = C.USERCREATED
				self.send['errors'],self.send['validation_rules'] = self.required_fields(serializer)
				return Response(self.send)
			self.send['message'] = "Invalid data !"
		else:
			self.send['message'] = C.USERALREADYEXIST

		self.send['errors'],self.send['validation_rules'] = self.required_fields(serializer)

		return Response(self.send)

	def required_fields(self,serializer):

		self.validation_rules 	 = {}
		self.errors = {}

		for key, value in  serializer.fields.items():
			self.validation_rules[key] = value.error_messages


		for key, value in serializer.errors.items():
			self.errors[key] = value[0]

		return self.errors,self.validation_rules


	#Update User
	def update(self,request,pk=0):
		self.tracking_user.info(f"{request.user} || Record-{pk} || Updated!")
		return Response({'message':'Updating Checking'})


	#Partial Update User
	def partial_update(self, request, pk=0):
		self.tracking_user.info(f"{request.user} || Record-{pk} || Partial Update!")
		return Response({'message':'Partially Update Checking'})


	#ON/OFF users status
	@action(detail=True,methods=['get'], url_name="useractivity")
	def useractivity(self,request,pk=0):
		try:
			user = User.objects.get(pk=pk)
		except User.DoesNotExist:
			pass
		else:
			user.is_active = False if user.is_active else True
			user.save()
			self.send['status']  = '1' ;
			self.send['message'] = C.ACTIVATED if user.is_active else C.DEACTIVATED ;

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