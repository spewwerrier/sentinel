from django.urls import path
from . import views
from . import incoming

urlpatterns = [
    path('', views.index),
    path('logs/', views.log),
    path('incoming/', incoming.index)
]
