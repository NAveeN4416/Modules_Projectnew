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
			 'product_images': ProductImages,
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
@Check_Login
#@Check_SuperUser
def Categories_List(request):

	context = {}

	context['title'] 	 = 'Categories List'
	context['page_name'] = 'categories'

	categories =  Categories.objects.all()
	context['categories'] = categories

	return render(request,'categories/categories_list.html',{'data':context})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@Check_Login
#@Check_SuperUser
def Add_Category(request,ref_id=0):

	user = request.user

	if not user.has_perm('products.add_categories',{'user':user}):
		return render(request,'403.html')

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
	context['page_name'] = 'categories'
	context['category']  = category
	return render(request,'categories/add_category.html',{'data':context})



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@Check_Login
#@Check_SuperUser
def View_Category(request,ref_id=0):

	context = {}
	context['title'] 	  = 'Category Details'
	context['page_name']  = 'categories'

	category =  Categories.objects.get(pk=ref_id) 
	subcategories = SubCategories.objects.filter(category=category)

	context['category']  = category
	context['subcategories'] = subcategories

	return render(request,'categories/view_category.html',{'data':context})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@Check_Login
#@Check_SuperUser
def Delete_Category(request,ref_id=0):

	user = request.user

	if not user.has_perm('products.delete_categories',{'user':user}):
		return render(request,'403.html')

	user = request.user

	if not user.has_perm('products.delete_categories',{'user':user}):
		return render(request,'403.html')

	category = table_obj('categories',ref_id)
	category.delete()

	return redirect('products:categories_list')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@Check_Login
#@Check_SuperUser
def Add_SubCategory(request,category_id=0,ref_id=0):

	user = request.user

	if not user.has_perm('products.add_subcategories',{'user':user}):
		return render(request,'403.html')

	context = {}
	context['title'] 	  = 'Add SubCategory'
	context['page_name']  = 'products'

	subcategory = table_obj('subcategories',ref_id)
	category    = table_obj('categories',category_id)

	if request.method == 'POST' :
		data  = request.POST.copy()
		category = Categories.objects.get(pk=data['category_id'])

		image = request.FILES.get('image',False)

		if image:
			old_image = category.image
			subcategory.image = image

		subcategory.category      = category
		subcategory.sub_category  = data['subcategory_name']
		subcategory.status 	      = data['status']
		subcategory.save();

	categories =  Categories.objects.filter(status=1)
	context['category']    = category
	context['categories']  = categories
	context['subcategory'] = subcategory

	return render(request,'sub_categories/add_sub_category.html',{'data':context})



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@Check_Login
#@Check_SuperUser
def View_SubCategory(request,ref_id=0):

	subcategory = SubCategories.objects.get(pk=ref_id) 
	products    = Products.objects.filter(subcategory=subcategory)

	context = {}
	context['title'] 	  = 'SubCategory Details'
	context['page_name']  = 'categories'

	context['subcategory']  = subcategory
	context['products'] 	= products

	return render(request,'sub_categories/view_subcategory.html',{'data':context})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@Check_Login
#@Check_SuperUser
def Delete_SubCategory(request,ref_id=0):

	user = request.user

	if not user.has_perm('products.delete_subcategories',{'user':user}):
		return render(request,'403.html')

	category = table_obj('subcategories',ref_id)
	category.delete()

	return redirect('products:categories_list')



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@Check_Login
#@Check_SuperUser
def Products_List(request):
	context = {}

	context['title'] 	 = 'Products List'
	context['page_name'] = 'products'

	return render(request,'products/products_list.html',{'data':context})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@Check_Login
#@Check_SuperUser
def Add_Product(request,subcategory_id=0,ref_id=0):

	sub_category = table_obj('subcategories',subcategory_id)
	product      = table_obj('products',ref_id)

	if request.method == 'POST' :
		data   = request.POST.copy()
		images = request.FILES.getlist('product_images')

		for image in images :
			product.image = image
			break

		product.product_name   = data['product_name']
		product.product_id 	   = "Product Id"
		product.price 		   = data['price']
		product.quantity 	   = data['quantity']
		product.address 	   = "Address"
		product.discount_price = data['discount_price']
		product.user 		   = request.user
		product.subcategory    = sub_category

		product.save()

		if product.id:
			product_images = ProductImages.objects.filter(product=product)

			if images:
				#Old Records
				if product_images:
					product_images.delete()

				for image in images:
					product_images = ProductImages()
					product_images.product = product
					product_images.image   = image
					product_images.status  = 1
					product_images.save()

		return redirect('products:view_subcategory',subcategory_id)

	context = {}

	context['sub_category'] = sub_category
	context['title'] 	 	= 'Add Product'
	context['page_name'] 	= 'categories'

	return render(request,'products/add_product.html',{'data':context})

