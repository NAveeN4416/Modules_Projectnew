from log_controller import Initiate_logging
import os
from django.shortcuts import render
from django.contrib.auth.models import User
from users.models import UserDetails
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from datetime import datetime
from django.db.models import Q
from django.contrib.auth.hashers import check_password
from apis import constants as C

from rest_framework.decorators import action
from rest_framework.response import Response
from .model_serializers import UserSerializer, UserMSerializer, UserdetailsSerializer
from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated


#Create a log path for this file
file_name = __name__.split('.')
file_path = '/'.join(file_name)
log_path  = f"logs/{file_path}/"
os.makedirs(log_path,exist_ok=True)


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

	#Tracking User Authentication
	report_name = f"{log_path}/Authentication"
	Log = Initiate_logging(report_name,10)
	authlog = Log.Track()

	#===Constructor============================
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.send    = {}

		self.send['status']  = 0
		self.send['message'] = "User Not found!"


	@action(detail=False,methods=['post'],url_name="user_login")
	def user_login(self,request):

		#if request.auth:
		#	self.send['message'] = f"You have already LoggedIn Mr.{request.user}"
		#	return Response(self.send)

		email    = request.POST.get('email',None)
		mobile   = request.POST.get('mobile',None)
		password = request.POST.get('password',None)

		user = User.objects.get(Q(username=email) | Q(email=email))
		if user :
			check_pass = check_password(password,user.password)

			if check_pass:
				self.send['status']  = 1
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

		if request.auth:
			user = request.user
			request.user.auth_token.delete()
			self.authlog.info(f"LoggedOut || {user} !")
			self.send['status']  = 1
			self.send['message'] = "Logged Out Successfully !" 

		return Response(self.send)


class UserMViewSet(viewsets.ModelViewSet):

	queryset         	   = User.objects.all()
	serializer_class 	   = UserMSerializer

	#authentication_classes = [TokenAuthentication]
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
		self.single_record  = False

		self.send['status']  = 0
		self.send['message'] = "User Not found!"
		self.send['data']    = {}


	#==Inherited Methods (Request Recievers)==
	#Get All Users
	def list(self,request):
		if request.auth:
			if self.ProcessUsers():
				users = self.userslist
				self.send['status']  = 1
				self.send['message'] = "success"
				self.send['data']    = users
			return Response(self.send)

		self.send['message'] = "Please login !"

		return Response(self.send)


	#Get Single User
	def retrieve(self,request,pk=0):
		self.single_record = True
		try:
			users = User.objects.get(pk=pk)
		except User.DoesNotExist:
			pass
		else:
			self.queryset = users
			if self.ProcessUsers():
				self.send['status']  = 1
				self.send['message'] = "success"
				self.send['data']    = self.userslist

			#Append user profile/details
			if self.ProcessUserDetails():
				details  = self.details
				self.send['data']['details'] = details

		return Response(self.send)


	#Delete User
	def destroy(self,request,pk=0):
		self.tracking_user.info(f"{request.user} ==> {pk} || Deleted!")
		return Response({'message':"You are trying to delete record id {}".format(pk)})


	#Create user
	def create(self,request):
		data = request.POST.copy()
		data.update({'date_joined':datetime.now()})

		users = User.objects.filter(Q(username=data['username']) | Q(email=data['email']))

		if not users:
			serializer = UserSerializer(data=data)
			if serializer.is_valid():
				instance = UserSerializer(serializer,data=data)
				serializer.save()
				self.send['message'] = C.USERCREATED
				return Response(self.send)
			self.send['message'] = serializer.errors
		else:
			self.send['message'] = C.USERALREADYEXIST
		
		return Response(self.send)


	#Update User
	def update(self,request,pk=0):
		return Response({'message':'Updating Checking'})


	#Partial Update User
	def partial_update(self, request, pk=0):
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
			self.send['status']  = 1 ;
			self.send['message'] = C.ACTIVATED if user.is_active else C.DEACTIVATED ;

		return Response(self.send)



	#===New Methods====
	def ProcessUserDetails(self):

		details  = UserDetails.objects.get(user=self.queryset)
		details  = UserdetailsSerializer(details)

		if details:
			self.details = details.data
			return True
		return False


	def ProcessUsers(self):

		users  = self.queryset

		if self.single_record:
			users = UserSerializer(users)
		else:
			users = UserSerializer(users,many=True)

		if users.data:
			self.userslist = users.data
			return True
		return False


#=====================Functions==========================================

