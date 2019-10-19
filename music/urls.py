from .import views
from django.urls import path, include
from django.conf.urls import url

app_name = "music"

urlpatterns = [
				url(r'welcome/',   views.welcome,   name="welcome"),
				url(r'player/(?P<album_id>\d+)$',     views.player,    name="player"),
				url(r'albums/',    views.albums, 	name="albums"),
				url(r'get_track/', views.get_track, name="get_track"),
			]
