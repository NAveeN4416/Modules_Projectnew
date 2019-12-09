from .import views
from django.urls import path, include
from django.conf.urls import url

app_name = "dashboard"


#DashboardApp Templates
urlpatterns = [
				url(r'^index/', views.Index, name="index"),
				url(r'^profile/', views.Profile, name="profile"),
				url(r'^terms/', views.TermsConditions, name="terms"),
				url(r'^users/$', views.Users_List, name="users_list"),
				url(r'^users/(?P<is_staff>\d+)$', views.Users_List, name="staff_list"),
				url(r'^user_details/(?P<user_id>\d+)$', views.User_Details, name="user_details"),
			  ]