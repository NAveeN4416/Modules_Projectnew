from .import views
from django.urls import path, include
from django.conf.urls import url

app_name = "dashboard"


#DashboardApp Templates
urlpatterns = [
				url(r'^index/', views.Index, name="index"),
				url(r'^terms/', views.TermsConditions, name="terms"),
			  ]