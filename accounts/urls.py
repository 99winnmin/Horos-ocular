from django.urls import path, include
from . import views

urlpatterns = [
    path('signup', views.register),
    path('find/password', views.find_password),
    path('login', views.login),
    path('logout', views.logout),
    path('info', views.user_info),
]