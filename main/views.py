from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, response
from django.shortcuts import redirect
from django.utils import timezone
from .models import ToDoList, CheckBox
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

def addVideo(response):
    #get the list of selected video links and selected list
    videoLinks = response.GET.getlist("Checked-Video")
    listName = response.GET.get("Checked-List")

    #if either aren't selected then refresh the home page
    if (listName is None) or len(videoLinks) == 0:
        return redirect('home')
    else:
        ls = ToDoList.objects.get(name = listName)
        #add all video links to the list and take user to view the list
        for video in videoLinks:
            ls.item_set.create(text=video, complete=False)
        return render(response, "main/index.html", {"ls": ls})


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
    #create two arrays of boxes, one for the videos and one for the lists, array of indexes
    vidBoxes, listBoxes, indexs = [], [], []
    for i in range(9):
        vidBoxes.append(CheckBox())
        listBoxes.append(CheckBox())
        indexs.append(i)

    userSearch = request.GET.get('search', '')
    videos = []
    vidCopy = []
    if userSearch != '':
        url = spaceReplace(userSearch)
        html = urllib.request.urlopen(url)
        videoIDS = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        for i in range(9):
            fullLink = "https://www.youtube.com/embed/" + videoIDS[i]
            videos.append(fullLink)
            vidCopy.append(fullLink)
    return render(request, "main/home.html", {"videos": zip(videos, vidBoxes, listBoxes, indexs), "copy": zip(vidCopy, indexs)})


def view(response):
    return render(response, "main/view.html", {})


def spaceReplace(search):
    search = re.sub(r"[^\w\s]", '', search)
    search = re.sub(r"\s+", '+', search)
    temp = "https://www.youtube.com/results?search_query=" + "learn" + search
    return temp
