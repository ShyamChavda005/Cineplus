from django.contrib import admin
from django.urls import path, include
from home import views
from movie import views as movie_views

urlpatterns = [
  path("",views.index,name="index"),
  path("about/",views.about,name="about"),
  path('search/',views.search,name='search'),
  path('movie/',movie_views.movies,name='movie'),
]
