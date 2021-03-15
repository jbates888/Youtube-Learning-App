from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, response
from django.utils import timezone
from .models import ToDoList
from .forms import CreateListForm
import re
from pytube import YouTube
import urllib.request
import requests
from django.conf import settings
from isodate import parse_duration

def index(response, id):
    ls = ToDoList.objects.get(id=id)

    if ls in response.user.todolist.all():
        if response.method == "POST":
            if response.POST.get("save"):
                for item in ls.item_set.all():
                    p = response.POST

                    if "clicked" == p.get("c"+str(item.id)):
                        item.complete = True
                    else:
                        item.complete = False

                    if "text" + str(item.id) in p:
                        item.text = p.get("text" + str(item.id))

                    item.save()

            elif response.POST.get("add"):
                newItem = response.POST.get("new")
                if newItem != "":
                    ls.item_set.create(text=newItem, complete=False)
                else:
                    print("invalid")

        return render(response, "main/index.html", {"ls": ls})
    return render(response, "main/home.html", {})

def create(response):
    if response.method == "POST":
        form = CreateListForm(response.POST)
        if form.is_valid():
            n = form.cleaned_data["name"]
            t = ToDoList(name=n)
            t.save()
            response.user.todolist.add(t)

            return HttpResponseRedirect("/%i" %t.id)
    else:
        form = CreateListForm()

    return render(response, "main/create.html", {"form":form})


def home(request):
    search_url = 'https://www.googleapis.com/youtube/v3/search'
    video_url = 'https://www.googleapis.com/youtube/v3/videos'

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


def view(response):
    return render(response, "main/view.html", {})


def spaceReplace(search):
    search = re.sub(r"[^\w\s]", '', search)
    search = re.sub(r"\s+", '+', search)
    temp = "https://www.youtube.com/results?search_query=" + "learn" + search
    return temp
