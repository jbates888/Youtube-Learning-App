from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from .models import ToDoList
from .forms import CreateListForm
import re
from pytube import YouTube
import urllib.request
import requests
from django.conf import settings
from isodate import parse_duration


def index(request, id):
    ls = ToDoList.objects.get(id=id)

    if request.method == "POST":
        if request.POST.get("save"):
            for item in ls.item_set.all():
                p = request.POST

                if "clicked" == p.get("c"+str(item.id)):
                    item.complete = True
                else:
                    item.complete = False

                if "text" + str(item.id) in p:
                    item.text = p.get("text" + str(item.id))

                item.save()

        elif request.POST.get("add"):
            newItem = request.POST.get("new")
            if newItem != "":
                ls.item_set.create(text=newItem, complete=False)
            else:
                print("invalid")

    return render(request, "main/index.html", {"ls": ls})


def get_name(request):
    if request.method == "POST":
        form = CreateListForm(request.POST)

        if form.is_valid():
            n = form.cleaned_data["name"]
            t = ToDoList(name=n, date=timezone.now())
            t.save()

            return HttpResponseRedirect("/%i" % t.id)

    else:
        form = CreateListForm()

    return render(request, "main/create.html", {"form": form})


def home(request):
    search_url = 'https://www.googleapis.com/youtube/v3/search'
    video_url = 'https://www.googleapis.com/youtube/v3/videos'

    # search_params = {
    # 	'part': 'snippet',
    # 	'q': 'learn python',
    # 	'key': settings.YOUTUBE_DATA_API_KEY,
    # 	'maxResults': 9,
    # 	'type': 'video',
    # }
    #
    # video_ids = []
    # r = requests.get(search_url, params=search_params)
    # results = r.json()['items']
    #
    # for result in results:
    # 	video_ids.append(result['id']['videoId'])
    #
    # video_params = {
    # 	'part': 'snippet,contentDetails',
    # 	'key': settings.YOUTUBE_DATA_API_KEY,
    # 	'id': ','.join(video_ids),
    # 	'maxResults': 9,
    # 	'type': 'video',
    # }
    #
    # r = requests.get(video_url, params=video_params)
    # results = r.json()['items']

    # for result in results:
    # 	print(result['snippet']['title'])
    # 	print(result['id'])

    userSearch = request.GET.get('search', '')
    videos = []
    if userSearch != '':
        url = spaceReplace(userSearch)
        html = urllib.request.urlopen(url)
        videoIDS = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        for i in range(9):
            fullLink = "https://www.youtube.com/embed/" + videoIDS[i]
            videos.append(fullLink)
    return render(request, "main/home.html", {"videos": videos})


def view(request):
    l = ToDoList.objects.all()
    return render(request, "main/view.html", {"lists": l})


def spaceReplace(search):
    search = re.sub(r"[^\w\s]", '', search)
    search = re.sub(r"\s+", '+', search)
    temp = "https://www.youtube.com/results?search_query=" + "learn" + search
    return temp
