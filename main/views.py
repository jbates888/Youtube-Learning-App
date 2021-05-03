import json
import random
import re
import urllib.request

import validators
from bs4 import BeautifulSoup
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from requests import get

from .forms import CreateListForm
from .models import CheckBox, ToDoList


#give users options to modify a list
def index(response, id):
    ls = ToDoList.objects.get(id=id)

    #check if the list is in the database
    if ls in response.user.todolist.all():
        if response.method == "POST":
            #if a user wants to save the current/modified list
            if response.POST.get("save"):
                for item in ls.item_set.all():
                    p = response.POST

                    if "text" + str(item.id) in p:
                        item.text = p.get("text" + str(item.id))

                    item.save()
            #if a user wants to add a new item to the list
            elif response.POST.get("add"):
                newItem = response.POST.get("new")
                if newItem != "":
                    #create a list item with the input text
                    ls.item_set.create(text=newItem, complete=False, video=False)
                else:
                    print("invalid")
            #if user wants to delete an item from a list
            elif response.POST.get("delete"):
                itemText = response.POST.get("delete")
                item = ls.item_set.get(id=itemText)
                print(item.delete())
        #send the user to view the list
        return render(response, "main/index.html", {"ls": ls})
    #send user to view an empty list
    return render(response, "main/home.html", {})

#add a video/webistes to a selected list
def addVideo(response):
    #get the video links, list name, and site links chosen by the user
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
            link = link.partition("(/)")
            title = link[0]
            weblink = link[2]
            print(weblink + "\n")
            ls.item_set.create(text=title, complete=False, video=False, siteLink=weblink, website=True)

        #take user to view the current list
        return render(response, "main/view.html", {"ls": ls, 'message': True})

#creating a list for a user
def create(response):
    if response.method == "POST":
        form = CreateListForm(response.POST)
        #check if the list already exists for the current user
        if form.is_valid() and response.user.todolist.filter(name=form.cleaned_data["name"]).exists():
            print("list already exists")
        #if the list doesn't exist, create and save it to the database
        elif form.is_valid():
            n = form.cleaned_data["name"]
            t = ToDoList(name=n)
            t.save()
            response.user.todolist.add(t)
            #send the user to view the empty list
            return HttpResponseRedirect("/%i" %t.id)
    else:
        form = CreateListForm()
    #send the user to create a list
    return render(response, "main/create.html", {"form":form})

#display videos and websites on the homepage for a search
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
    results = search(userSearch, num_results = 50)
    chosenIndexes = []
    try:
        #get a list of random indexes to choose websites
        chosenIndexes = random.sample(range(1, int(len(results)/2)), 10)
    except ValueError:
        print("Sample size exceeded population size")
    newResults = []
    for x in chosenIndexes:
        soup = BeautifulSoup('"{}"'.format((results[x])[1]), features = "html.parser")
        # get the tile from the <h3> tag
        title = soup.get_text()
        valid = validators.url((results[x])[0])
        # confirm that the url is valid
        if valid:
            newResults.append(((results[x])[0], title))
        else:
            print("Invalid url")

    videos = []
    titles = []
    vidCopy = []
    if userSearch != '':
        #get the video id's from the youtube page from the user search
        url = spaceReplace(userSearch)
        html = urllib.request.urlopen(url)
        videoIDS = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        #loop over 9 of the videos
        for i in range(9):
            fullLink = "https://www.youtube.com/embed/" + videoIDS[i]
            params = {"format": "json", "url": "https://www.youtube.com/watch?v=%s" % videoIDS[i]}
            url = "https://www.youtube.com/oembed"
            query_string = urllib.parse.urlencode(params)
            url = url + "?" + query_string
            #getting the video title from the youtube page
            with urllib.request.urlopen(url) as response:
                response_text = response.read()
                data = json.loads(response_text.decode())
                titles.append(data['title'])

            videos.append(fullLink)
            vidCopy.append(fullLink)
    #send the user to view the selected items in the list that was selected
    return render(request, "main/home.html", {"videos": zip(videos, vidBoxes, listBoxes, indexs), "copy": zip(vidCopy, indexs, titles), "sites": newResults})

#deleting a list for a user
def view(response):
    message = False
    if response.method == "POST":
        if response.POST.get("delete"):
            print("delete list")
            #deleting a list
            try:
                ls = ToDoList.objects.get(id=response.POST.get("delete"))
                message = True
                ls.delete()
            except:
                print("list already deleted")
    #send user back to view all of the lists
    return render(response, "main/view.html", {'message_name': message})

#modifying a search to be
def spaceReplace(search):
    #replace non-searchable characters in the search
    search = re.sub(r"[^\w\s]", '', search)
    search = re.sub(r"\s+", '+', search)
    #attatch the search onto a full youtube link
    temp = "https://www.youtube.com/results?search_query=" + "learn" + search
    return temp

#searching google for websites from the passed in search
def search(term, num_results=8, lang="en"):
    usr_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/61.0.3163.100 Safari/537.36'}

    #fetch the results from google
    def fetch_results(search_term, number_results, language_code):
        escaped_search_term = search_term.replace(' ', '+')

        google_url = 'https://www.google.com/search?q={}&num={}&hl={}'.format(escaped_search_term, number_results+1,
                                                                              language_code)
        #get the source code
        response = get(google_url, headers=usr_agent)
        response.raise_for_status()

        return response.text

    #parse the results from the html
    def parse_results(raw_html):
        soup = BeautifulSoup(raw_html, 'html.parser')
        result_block = soup.find_all('div', attrs={'class': 'g'})
        #loop over all of the results in the google search
        for result in result_block:
            link = result.find('a', href=True)
            title = result.find('h3')
            #attatch the link and title for the website to be returned
            if link and title:
                yield link['href'], title

    #get the html for the search
    html = fetch_results(term, num_results, lang)
    #return a list of titles and linkes
    return list(parse_results(html))
