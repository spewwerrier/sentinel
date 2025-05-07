from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from django.template import loader

def index(request: HttpRequest):
    return render(request, 'server/index.html')

def block(request: HttpRequest):
    return render(request, 'server/blocked.html')
