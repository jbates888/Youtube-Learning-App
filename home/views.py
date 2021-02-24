from django.shortcuts import render
from django.http import HttpResponse
from .models import VideoList, Video, User

def home(request, name):
    ls = VideoList.objects.get(name=name)
    videos = ls.video_set.get(id=1)
    return HttpResponse("<h1>%s</h1><br></br><p>%s</p>" % (ls.name, str(videos.url)))

#def account(response):
#    return HttpResponse('<h1>Account Page</h1>')
