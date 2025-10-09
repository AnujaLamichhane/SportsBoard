from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
def home(request):
    # context = {
    #     "page_title": "Django Day 2",
    #     "message": "Welcome to Day 2 of Django!"
    # }
    # return HttpResponse("Welcome to Django Workshop!")
    return render(request, 'homepage/home.html')
def about(request):
    return HttpResponse("Welcome to about page.")