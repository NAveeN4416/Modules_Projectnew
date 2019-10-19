from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Industry, Artist, Album, Track

# Create your views here.

def welcome(request):
	return render(request,'site/welcome.html')


def player(request,album_id):
	album = Album.objects.filter(pk=album_id)[0]
	context = {}
	context['album_id'] = album_id
	context['album'] = album
	return render(request,'site/player.html',context=context)


def albums(request):
	albums = Album.objects.all()
	context = {}
	context['albums'] = albums
	return render(request,'site/albums.html',context=context)


def get_track(request):
	album_id = request.POST.get('album_id')
	tracks =  Track.objects.filter(album_id=album_id)
	data = []
	for track in tracks:
		d = {}

		m, s = divmod(track.length, 60)

		d['id']     = track.id
		d['name']   = track.name
		d['length'] = f"{m:02d}:{s}"
		d['file']   = track.file.url 

		data.append(d)
	return JsonResponse(data,safe=False)
