from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.core.signals import request_finished, request_started
from django.contrib.auth import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from .models import UserDetails
from django.conf  import settings



@receiver(post_save,sender=User)
def set_useractivity(sender,*args,**kwargs):
	if kwargs['created']:
		user = kwargs['instance']
		user.is_active = 0
		user.save()


@receiver(user_logged_in)
def set_login_flag(sender,user,request,**kwargs):
	if user:
		print(f"{user} logged in just now")


@receiver(user_logged_out)
def set_logout_flag(sender,user,request,**kwargs):
	print(f"{user} logged out just now")


# @receiver(request_started)
# def request_started(sender,*args,**kwargs):
# 	print("Request Started")


# @receiver(request_finished)
# def request_finished(sender,**kwargs):
# 	print("Request Finished")
