import os
from datetime import datetime
from django.utils import timezone
from django.shortcuts import render,redirect
from django.http import HttpRequest, HttpResponse ,JsonResponse
from .forms import UserRegistration, Forms_Demo
import json
from django.contrib.auth.models import User, Group, Permission
from .models import UserDetails
from users import constants as C
from django.contrib.auth import login as auth_login, logout as logout_user, get_user
from django.contrib.auth import authenticate as check_credentails
from django.contrib.auth.hashers import check_password
from django.contrib.sessions.models import Session
from django.contrib import messages

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils import six
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.db.models import Q
from django.conf import settings
from django.urls import reverse
from django.db import IntegrityError, transaction, DatabaseError

from core_modules.decors import Set_RequestObject, Check_Login, CheckUser
#==================================Views START================================================

#Create a log path for this file
file_name = __name__.split('.')
file_path = '/'.join(file_name)
log_path  = f"logs/{file_path}/"
os.makedirs(log_path,exist_ok=True)



#Forms Demo
#@Check_Login
def forms_demo(request):

	form = Forms_Demo()

	if request.method == 'POST' :
		data = request.POST.copy()
		data.update({'image':request.FILES.get('image')})
		print(data)
		form = Forms_Demo(data)
		if form.is_valid():
			return HttpResponse("Yes, Valid :)")

	form = form.as_p()

	response =  render(request,'forms_demo.html',{'form':form})

	#response.set_cookie('last_connection',datetime.now())
	#request.session['username'] = "Naveen"

	return response


def download_image(request):

	user = UserDetails.objects.get(pk=27)

	try:
		file_name = os.path.basename(user.image.name)
		response = HttpResponse(user.image, content_type='image/png')
		response['Content-Disposition'] = f'attachment; filename={file_name}'
		return response
	except ValueError :
		return HttpResponse("Sorry, File not found !")


	# import eyed3

	# audiofile = eyed3.load('example.mp3')
	# if (audiofile.tag == None):
	#     audiofile.initTag()

	# audiofile.tag.images.set(3, open('cover.jpg','rb').read(), 'image/jpeg')

	# audiofile.tag.save()


#Registration
@transaction.atomic
def register(request):

	form = UserRegistration()

	if request.method=='POST': #if post method then try to insert data
		
		check_user = User.objects.filter(Q(username=request.POST.get('username')) | Q(email=request.POST.get('email')))

		if not check_user:
			form = UserRegistration(request.POST)

			if form.is_valid():

				if form.save(): #//if user saved then save details
					username = form.cleaned_data.get('username')
					user = User.objects.get(username=username)

					#Creating UserDetails object
					try:
						with transaction.atomic():
							user_details 				= UserDetails()
							user_details.user 			= user
							user_details.image 			= None
							user_details.phone_number 	= form.cleaned_data.get('phone_number')
							user_details.address 		= 'empty'
							user_details.auth_level 	= 1
							user_details.device_type 	= 'website'
							user_details.device_token 	= 'empty'
							user_details.role 			= 'customer'

							user_details.save(); #Insert data into userdetails table

					except (IntegrityError,DatabaseError):
						handle_exception()

					send_mail(request,user.id,'Django Account Verification','activate_account')
					messages.info(request,"Please login here !")
					return redirect('users:login')
		else:
			messages.info(request,"User already exists with same username or email")

	errors = load_form_errors(form)
	return render(request,'register.html',{'form':form,'err':errors})


#Login
def login(request):
	if request.user.is_authenticated:
		if request.user.is_superuser:
			return redirect('dashboard:index')
		return redirect(settings.LOGIN_REDIRECT_URL)

	if request.method == 'GET':
		request.session['redirect_url'] = request.GET.get(settings.URL_REDIRECT_NAME)
		#return HttpResponse(request.session.get('redirect_url'))

	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')

		login_flag = authenticate(request,username,password)

		if login_flag == C.AUTH_SUCCESS:
			user = User.objects.get(username=username)
			user.email_user('Django | Login Alert','Your Account has been accessed !')
			auth_login(request,user)
			if user.is_staff:
				if request.session['redirect_url']:
					return redirect(request.session['redirect_url'])

				return redirect('dashboard:index')

			return redirect(settings.LOGIN_REDIRECT_URL)

	return render(request,'login.html',)


#Logout
@Set_RequestObject
def logout(request):
    if request.user.is_authenticated:
      logout_user(request)
      # user_id = request.user.pk
      # unexpired_sessions = Session.objects.filter(expire_date__gte=timezone.now())
      # [
      #   session.delete() for session in unexpired_sessions
      #   if str(user_id) == session.get_decoded().get('_auth_user_id')
      # ]
      messages.success(request,"Logged out Successfully !")
      # print(request.current_app)
    return redirect('users:login')


def users_list(request):
	if request.user.has_perm('users.view_users'):
		users_list = User.objects.all()
		return render(request,'users_list.html',{'users':users_list})
	return HttpResponse("You can't these details !")


#Dashboard
@Check_Login
@CheckUser
def dashboard(request):
	return render(request,'dashboard.html')



def generate_users_record(request,format='json'):
	from django.core import serializers	
	users = User.objects.all()
	groups = Group.objects.all()
	persmissions = Permission.objects.all()

	XMLSerializer = serializers.get_serializer(format)
	xml_serializer = XMLSerializer()

	objects = {}

	objects['user_data'] = xml_serializer.serialize(users)
	objects['group_data'] = xml_serializer.serialize(groups)
	objects['persmission_data'] = xml_serializer.serialize(persmissions)

	path = 'user_db_records'

	for k,v in objects.items():
		with open(f"{path}/{k}.{format}", "w",encoding='utf-8') as file:
			file.write(v)


	return HttpResponse('FILES GENERATED')



#Send Verification Link
def send_verification_link(request):

	if request.method == 'POST':
		username = request.POST.get('username')

		try:
			searched = User.objects.filter(Q(username=username) | Q(email=username))
			
			if len(searched)==1:
				user = searched[0]
				send_mail(request,user.id,'Django Account Verification','activate_account')
				messages.success(request,C.VERFMAIL_SENT)
				return redirect('users:login')
			else:
				messages.info(request,C.USERNOT_FOUND)
		except User.DoesNotExist:
			messages.info(request,C.USERNOT_FOUND)

	return render(request,'send_verification_link.html')



#Forgot Password
def forgot_password(request):

	if request.method == 'POST':
		username = request.POST.get('username')

		try:
			searched = User.objects.filter(Q(username=username) | Q(email=username))
			
			if len(searched)==1:
				user = searched[0]
				send_mail(request,user.id,'Django Reset Password','change_password')
				messages.success(request,C.RESET_PASSWORDLINK)
				return render(request,'forgot_password.html')
			else:
				messages.info(request,C.USERNOT_FOUND)
		except User.DoesNotExist:
			messages.info(request,C.USERNOT_FOUND)

	return render(request,'forgot_password.html')


#Change Password
def change_password(request,uidb64, token):
    try:
      uid  = urlsafe_base64_decode(uidb64).decode()
      user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
      user = None

    if user is not None and account_activation_token.check_token(user, token):
    	context = {}
    	context['user'] = user.username
    	context['uid']  = user.id
    	return render(request,'change_password.html',context)
    else:
    	return HttpResponse(C.INVALID_LINK)



#Set Password
def set_password(request):
	if request.method == 'POST':
		password  = request.POST['password']
		password2 = request.POST['password2']

		user_id  = request.POST['uid']
		user     = User.objects.get(id=user_id)
		if user.id:
			user.set_password(password)
			user.save()
			messages.info(request,C.PASSWORD_RESET_SUCCESS)
		else:
			pass
			#messages.info(request,C.PASSWORD_RESET_SUCCESS)
		return redirect('users:login')


#Activate Account
def activate_account(request, uidb64, token):
    try:
      uid  = urlsafe_base64_decode(uidb64).decode()
      user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
      user = None

    if user is not None and account_activation_token.check_token(user, token):
    	user.is_active = True
    	user.save()
    	messages.success(request,C.ACCOUNT_ACTIVATED)
    	return redirect('users:login')
    else:
    	return HttpResponse(C.INVALID_LINK)


#==================================Views END======================================================


#=============================Helping Methods==================================
def load_form_errors(form_obj):

	json_data = form_obj.errors.as_json(escape_html=False)
	data 	  = json.loads(json_data)

	errors = {}
	for field, error in data.items():
		errors[field] = error[0]['message']

	return errors


def authenticate(request,username,password):
	try:
		user = User.objects.get(username=username)

		check_pass = check_credentails(username=username,password=password)
		#check_pass = check_password(password,user.password)

		if check_pass:
			if user.is_active:
				return C.AUTH_SUCCESS
			messages.warning(request,C.ACCOUNT_INACTIVE)
			return C.USER_INACTIVE
		else:
			messages.warning(request,C.INVALID_PASSWORD)
			return C.INCORRECT_PASSWORD

	except User.DoesNotExist:
		messages.info(request,C.USERNOT_FOUND)
		return C.USERNOTEXIST


def send_mail(request,user_id,subject,return_path):
	user  = User.objects.get(pk=user_id)
	email = user.email
	current_site = get_current_site(request)

	context = {
	            'user'  : user.username,
	            'domain': current_site.domain,
	            'uid'   : urlsafe_base64_encode(force_bytes(user.pk)).decode(),
	            'token' : account_activation_token.make_token(user),
	            'path'  : 'users:'+return_path,
	          }

	html_pages = {
					'activate_account' : 'verify_email.html',
					'change_password'  : 'verify_email.html',
			  	  }

	message = render_to_string(html_pages[return_path], context)
	send    = EmailMessage(subject, message, to=[email])

	if send.send():
		return 1
	return 0


class TokenGenerator(PasswordResetTokenGenerator):

  def _make_hash_value(self, user, timestamp):
    return (
              six.text_type(user.pk) + six.text_type(timestamp) +
              six.text_type(user.username)  )


account_activation_token = TokenGenerator()
