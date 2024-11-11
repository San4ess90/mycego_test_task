from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('files/', views.list_files, name='list_files'),
    path('download/', views.download_file, name='download_file'),
]