from django.shortcuts import render, redirect
# from django.contrib.auth.models import User
from movie.models import *

# Create your views here.

def index(request) :    
    return render(request,"index.html")

def about(request) :
    return render(request,"about.html")

def search(request):
    query = request.GET.get('query')
    results = []

    if query:
        results = Movie.objects.filter(name__icontains=query)

    return render(request, 'search_movies.html', {'query': query, 'results': results})

