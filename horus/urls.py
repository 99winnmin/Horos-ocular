from django.urls import path, include
from . import views

urlpatterns = [
    path('video/all', views.get_videos),
    path('video/index', views.get_indexed_data),
    path('video/registration', views.input_video),
    path('video/search', views.search_person),
    path('video/info', views.get_video_info),
    path('video/stt', views.get_stt_data),
]