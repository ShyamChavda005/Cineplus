from django.shortcuts import render, redirect
# from django.contrib.auth.models import User
from movie.models import *
from datetime import *

# Create your views here.

def index(request) :    
    today = date.today()
    today_shows = Theater.objects.filter(datetime__date=today).select_related("movie")

    grouped_shows = {}
    for show in today_shows:
        movie = show.movie
        if movie not in grouped_shows:
            grouped_shows[movie] = []
        grouped_shows[movie].append(show)
    
    return render(request,"index.html",{'grouped_shows': grouped_shows})

def about(request) :
    return render(request,"about.html")

def search(request):
    query = request.GET.get('query')
    results = []

    if query:
        results = Movie.objects.filter(name__icontains=query)

    return render(request, 'search_movies.html', {'query': query, 'results': results})

