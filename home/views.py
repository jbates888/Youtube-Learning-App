from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse('<h1>Home Screen</h1>')

def account(response):
    return HttpResponse('<h1>Account Page</h1>')
