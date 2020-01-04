from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.core.signals import request_finished, request_started
from django.contrib.auth import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from .models import UserDetails
from django.conf  import settings
from log_controller import Initiate_logging
import os

#Create a log path for this file
log_path  = f"logs/users/views"
os.makedirs(log_path,exist_ok=True)


@receiver(post_save,sender=User)
def set_useractivity(sender,*args,**kwargs):
	if kwargs['created']:
		user = kwargs['instance']
		user.is_active = 0
		user.save()
		print("Signal Called")


@receiver(user_logged_in)
def login_signal(sender,user,request,**kwargs):
	if user:
		report_name = f"{log_path}/LoginSignals"
		Log = Initiate_logging(report_name,10)
		tracking_user = Log.Track()
		tracking_user.info(f"{user} logged in just now")


@receiver(user_logged_out)
def logout_signal(sender,user,request,**kwargs):
	report_name = f"{log_path}/LogoutSignals"
	Log = Initiate_logging(report_name,10)
	tracking_user = Log.Track()
	tracking_user.info(f"{user} logged out just now")


@receiver(user_login_failed)
def login_failed_signal(sender,credentials,request,**kwargs):
	print('Login failed')


@receiver(request_started)
def request_started(sender,*args,**kwargs):
	print("Request Started Signal called")


@receiver(request_finished)
def request_finished(sender,**kwargs):
	print("Request Finished Signal called")
