from django.db import models

# Create your models here.


class DashboardSettings(models.Model):

	authorisation_keys = models.TextField(blank=True,null=True)
	