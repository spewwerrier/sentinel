from django.urls import path
from . import views
from . import ebpf_data

urlpatterns = [
    path('', views.index),
    path('filterip', views.filter_option),
    path('incoming/', ebpf_data.incoming),
    path('filter', ebpf_data.filter)
]
