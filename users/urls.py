from .import views
from django.urls import path, include
from django.conf.urls import url

app_name = "users"

urlpatterns = [
				url(r'^register/',  		     views.register,  					name="register"),
				url(r'^login/',     		     views.login,     					name="login"),
				url(r'^logout/',    		     views.logout,    					name="logout"),
				url(r'^dashboard/', 		     views.dashboard, 					name="dashboard"),
				url(r'^send_verification_link/', views.send_verification_link, 		name="send_verification_link"),
				url(r'^forgot_password/',        views.forgot_password, 		    name="forgot_password"),
				url(r'^set_password/',           views.set_password, 		        name="set_password"),
				url(r'^activate_account/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',  views.activate_account,  name="activate_account"),
				url(r'^change_password/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',  views.change_password,  name="change_password"),
			  ]


urlpatterns += [
					url(r'^users_list/', views.users_list, name="users_list"),
				]