import os

from django.utils import timezone
from django.shortcuts import render,redirect
from django.http import HttpRequest, HttpResponse ,JsonResponse
#from .forms import UserRegistration
from products.models import Products, ProductImages, Categories, SubCategories
import json
from django.contrib.auth.models import User, Permission
from django.views.decorators.cache import cache_control
from users.models import UserDetails
from users import constants as C
from django.contrib.auth import login as auth_login, logout
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

from django.db import IntegrityError, transaction, DatabaseError

from core_modules.decors import Set_RequestObject, Check_Login, Check_SuperUser
#==================================Views START================================================


#Create a log path for this file
file_name = __name__.split('.')
file_path = '/'.join(file_name)
log_path  = f"logs/{file_path}/"
os.makedirs(log_path,exist_ok=True)



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@Check_Login
#@Check_SuperUser
def Index(request):
	context = {}

	context['title'] 	 = 'Dashboard'
	context['page_name'] = 'dashboard'

	return render(request,'dashboard/index.html',{'data':context})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@Check_Login
#@Check_SuperUser
def Profile(request):
	context = {}

	context['title'] 	 = 'Profile'
	context['page_name'] = 'profile'

	return render(request,'dashboard/profile.html',{'data':context})



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@Check_Login
def TermsConditions(request):
	context = {}

	context['title'] 	 = 'Terms & Conditions'
	context['page_name'] = 'terms'

	return render(request,'dashboard/terms_conditions.html',{'data':context})



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@Check_Login
def Users_List(request,is_staff=0):
	context = {}
	title = "User's List" if is_staff==0 else "Staff List" 
	context['title'] 	 = title
	context['page_name'] = 'users'
	context['users'] = User.objects.filter(is_staff=is_staff).exclude(username='admin')

	return render(request,'users/users_list.html',{'data':context})



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@Check_Login
def User_Details(request,user_id):
	context = {}
	context['title'] 	 = 'User Details'
	context['page_name'] = 'users'

	user = User.objects.get(id=user_id)
	user.permissions = Permission.objects.filter(user=user)
	user.all_groups = user.groups.all()

	context['user'] = user

	return render(request,'users/user_details.html',{'data':context})

