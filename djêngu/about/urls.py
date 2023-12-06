from django.urls import path

from . import views

urlpatterns = [
    path('me', views.aboutPage,name='about-me'),
]