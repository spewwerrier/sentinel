from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from django.template import loader

def index(request: HttpRequest):
    return render(request, 'server/index.html')


def log(request: HttpRequest):
    return HttpResponse("logging bzzt bzzt")
