from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, response
from django.shortcuts import redirect
from django.utils import timezone
from .models import ToDoList, Item, CheckBox
from .forms import CreateListForm
import re
from pytube import YouTube
import urllib.request
# from googlesearch import search
import requests
from django.conf import settings
from isodate import parse_duration
from django.contrib import messages
from bs4 import BeautifulSoup
import validators
from requests import get

def index(response, id):
    ls = ToDoList.objects.get(id=id)

    if ls in response.user.todolist.all():
        if response.method == "POST":
            if response.POST.get("save"):
                for item in ls.item_set.all():
                    p = response.POST

                    if "text" + str(item.id) in p:
                        item.text = p.get("text" + str(item.id))

                    item.save()

            elif response.POST.get("add"):
                newItem = response.POST.get("new")
                if newItem != "":
                    ls.item_set.create(text=newItem, complete=False, video=False)
                else:
                    print("invalid")
            elif response.POST.get("delete"):
                itemText = response.POST.get("delete")
                item = ls.item_set.get(id=itemText)
                print(item.delete())
        return render(response, "main/index.html", {"ls": ls})
    return render(response, "main/home.html", {})

def addVideo(response):
    #get the list of selected video links and selected list
    videoLinks = response.GET.getlist("Checked-Video")
    listName = response.GET.get("Checked-List")
    siteLinks = response.GET.getlist("Checked-Site")

    #if either aren't selected then refresh the home page
    if (listName is None) or (len(videoLinks) == 0 and len(siteLinks) == 0):
        return redirect('create')
    else:
        ls = ToDoList.objects.get(name = listName)
        #add all video links to the list
        for video in videoLinks:
            ls.item_set.create(text=video, complete=False, video=True, website=False)

        #add all website links and their title to the list
        for link in siteLinks:
            title = link.split("/")[0]
            link = link.split("/")[1]
            ls.item_set.create(text=title, complete=False, video=False, siteLink=link, website=True)

        #take user to view the current list
        return render(response, "main/view.html", {"ls": ls, 'message': True})

def create(response):
    if response.method == "POST":
        form = CreateListForm(response.POST)
        if form.is_valid() and response.user.todolist.filter(name=form.cleaned_data["name"]).exists():
            print("list already exists")
        elif form.is_valid():
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
        indexs.append(i + 1)

    userSearch = request.GET.get('search', '')

    # get websites related to the search
    results = search(userSearch, num_results = 25)
    newResults = []
    for t in results:
        soup = BeautifulSoup('"{}"'.format(t[1]))
        #get the tile from the <h3> tag
        title = soup.get_text()
        valid = validators.url(t[0])
        #confirm that the url is valid
        if valid:
            newResults.append((t[0], title))
        else:
            print("Invalid url")

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

    return render(request, "main/home.html", {"videos": zip(videos, vidBoxes, listBoxes, indexs), "copy": zip(vidCopy, indexs), "sites": newResults})


def view(response):
    if response.method == "POST":
        if response.POST.get("delete"):
            print("delete list")
            ls = ToDoList.objects.get(id=response.POST.get("delete"))
            print(ls.delete())

    return render(response, "main/view.html", {})


def spaceReplace(search):
    search = re.sub(r"[^\w\s]", '', search)
    search = re.sub(r"\s+", '+', search)
    temp = "https://www.youtube.com/results?search_query=" + "learn" + search
    return temp

def search(term, num_results=10, lang="en"):
    usr_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/61.0.3163.100 Safari/537.36'}

    def fetch_results(search_term, number_results, language_code):
        escaped_search_term = search_term.replace(' ', '+')

        google_url = 'https://www.google.com/search?q={}&num={}&hl={}'.format(escaped_search_term, number_results+1,
                                                                              language_code)
        response = get(google_url, headers=usr_agent)
        response.raise_for_status()

        return response.text

    def parse_results(raw_html):
        soup = BeautifulSoup(raw_html, 'html.parser')
        result_block = soup.find_all('div', attrs={'class': 'g'})
        for result in result_block:
            link = result.find('a', href=True)
            title = result.find('h3')
            if link and title:
                yield (link['href'], title)

    html = fetch_results(term, num_results, lang)
    return list(parse_results(html))
