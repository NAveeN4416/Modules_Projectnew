from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserDetails(models.Model):

	user  		   = models.OneToOneField(User,related_name="user_details", on_delete=models.CASCADE)
	image 		   = models.FileField(upload_to='user_profilepics')
	phone_number   = models.CharField(max_length=10)
	gender		   = models.IntegerField(default=0)
	address        = models.CharField(max_length=50)
	auth_level     = models.IntegerField(default=1)
	device_type    = models.CharField(max_length=20)
	device_token   = models.CharField(max_length=150)
	role   		   = models.CharField(max_length=20)

	def __str__(self):
		return '{}'.format(self.user.first_name)