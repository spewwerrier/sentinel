from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from django.template import loader

# in this program views.py are used for rendering a HTML template
# other request are done by ebpf_data.py
def index(request: HttpRequest):
    return render(request, 'server/index.html')

def block(request: HttpRequest):
    return render(request, 'server/blocked.html')
