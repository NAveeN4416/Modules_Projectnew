from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Industry, Artist, Album, Track

from requests_html_test import HTML, HTMLSession,AsyncHTMLSession
from threading import Thread
import requests
import  os
import asyncio
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

results = ''

async def render_movie():
	global results
	session = AsyncHTMLSession()
	results = await session.get(f"https://isongs.info/?label=&q=nuvu+naku+nachav")
	results.html.render()


def search_movie(request):

	if request.method=='POST':
		movie_name = request.POST.get('movie_name').replace(' ','+')

		loop = asyncio.new_event_loop()
		asyncio.set_event_loop(loop)
		loop = asyncio.get_event_loop()
		loop.run_until_complete(render_movie())
		asyncio.sleep(10)
		return HttpResponse(results.html.html)

	return render(request,'site/search_form.html')

