import os
from django.utils import timezone
from django.shortcuts import render,redirect
from django.http import HttpRequest, HttpResponse ,JsonResponse
#from .forms import UserRegistration
from products.models import Products, ProductImages, Categories, SubCategories
import json
from django.contrib.auth.models import User
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
from datetime import datetime
from django.db import IntegrityError, transaction, DatabaseError

from core_modules.decors import Set_RequestObject, Check_Login, Check_SuperUser


#=============== Product Views =======================================================
# Model Constants
contants = {
			 'products'      : Products,
			 'categories'    : Categories,
			 'subcategories' : SubCategories,
			} 


def table_obj(table_name,ref_id):
    if ref_id:
        obj   = contants[table_name].objects.get(id=ref_id)
    else:
        obj   = contants[table_name]()
    return obj


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@Set_RequestObject
@Check_Login
@Check_SuperUser
def Categories_List(request):

	context = {}

	context['title'] 	 = 'Categories List'
	context['page_name'] = 'products'

	categories =  Categories.objects.filter(status=1) 
	context['categories'] = categories

	return render(request,'categories/categories_list.html',{'data':context})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@Set_RequestObject
@Check_Login
@Check_SuperUser
def Add_Category(request,ref_id=0):

	category = table_obj('categories',ref_id)

	if request.method == 'POST' :
		data  = request.POST.copy()

		image = request.FILES['image']

		if image:
			old_image = category.image
			category.image = image

		category.category_name = data['category_name']
		category.status 	   = data['status']

		category.save()

		return redirect('products:categories_list')

	context = {}

	context['title'] 	 = 'Add Category'
	context['page_name'] = 'products'
	context['category']  = category
	return render(request,'categories/add_category.html',{'data':context})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@Set_RequestObject
@Check_Login
@Check_SuperUser
def Delete_Category(request,ref_id=0):
	category = table_obj('categories',ref_id)
	category.delete()

	return redirect('products:categories_list')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@Set_RequestObject
@Check_Login
@Check_SuperUser
def SubCategories_list(request):

	context = {}

	context['title'] 	 = 'SubCategories List'
	context['page_name'] = 'products'

	subcategories =  SubCategories.objects.filter(status=1) 
	context['subcategories'] = subcategories

	return render(request,'sub_categories/sub_categories_list.html',{'data':context})



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@Set_RequestObject
@Check_Login
@Check_SuperUser
def Add_SubCategory(request,ref_id=0):

	context = {}
	context['title'] 	  = 'Add SubCategory'
	context['page_name']  = 'products'

	subcategory = table_obj('subcategories',ref_id)

	if request.method == 'POST' :
		data  = request.POST.copy()
		category = Categories.objects.get(pk=data['category_id'])

		subcategory.category      = category
		subcategory.sub_category  = data['subcategory_name']
		subcategory.status 	      = data['status']
		subcategory.image 		  = request.FILES['image']
		subcategory.save();

	categories =  Categories.objects.filter(status=1) 
	context['categories']  = categories
	context['subcategory'] = subcategory

	return render(request,'sub_categories/add_sub_category.html',{'data':context})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@Set_RequestObject
@Check_Login
@Check_SuperUser
def Products_List(request):
	context = {}

	context['title'] 	 = 'Products List'
	context['page_name'] = 'products'

	return render(request,'products/products_list.html',{'data':context})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@Set_RequestObject
@Check_Login
@Check_SuperUser
def Add_Product(request):

	if request.method == 'POST' :
		data  = request.POST.copy()
		files = request.FILES.getlist('product_images')
		return HttpResponse(data)

		product = Products(data)

		product['user'] = request.user
		product['subcategory'] = SubCategories()

	context = {}

	context['title'] 	 = 'Add Product'
	context['page_name'] = 'products'

	return render(request,'products/add_product.html',{'data':context})

