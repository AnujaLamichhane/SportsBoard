from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
def home(request):
    return render(request, 'homepage/home.html')
    # return HttpResponse("Homepage is working!")

def about(request):
    return HttpResponse("Welcome to about page.")

