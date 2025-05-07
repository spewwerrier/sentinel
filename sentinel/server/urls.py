from django.urls import path
from . import views
from . import ebpf_data

urlpatterns = [
    path('', views.index),
    path('block/', views.block),
    path('incoming/', ebpf_data.incoming),
    path('blocked/', ebpf_data.blocked),
    path('filter', ebpf_data.filter)
]
