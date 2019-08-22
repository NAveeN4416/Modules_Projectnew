from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import UserDetails


@receiver(post_save,sender=User)
def set_useractivity(sender,*args,**kwargs):
	if kwargs['created']:
		user = kwargs['instance']
		user.is_active = 0
		user.save()
