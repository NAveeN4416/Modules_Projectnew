from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.core.signals import request_finished, request_started
from django.contrib.auth import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from .models import Categories, SubCategories, Products, ProductImages
from django.conf  import settings


@receiver(pre_save, sender=Categories)
def pre_save_category(sender,**kwargs):
	print(kwargs)


@receiver(post_save, sender=Categories)
def post_save_category(sender,**kwargs):
	print(kwargs)
