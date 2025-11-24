from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
def home(request):
    return render(request, 'homepage/home.html')
    # return HttpResponse("Homepage is working!")

def about(request):
    return render(request, 'homepage/about.html')
def cricket(request):
    return HttpResponse("Welcome to cricket page.")
def football(request):
    return HttpResponse("Welcome to football page.")
def volleyball(request):
    return HttpResponse("Welcome to volleyball page.")
def basketball(request):
    return HttpResponse("Welcome to basketball page.")
def badminton(request):
    return HttpResponse("Welcome to badminton page.")
# def table_tennish(request):
#     return HttpResponse("Welcome to table_tennish page.")

# from django.shortcuts import render, get_object_or_404
# from datetime import date
# from .models import Match

# def home(request):
#     featured_matches = Match.objects.filter(date__gte=date.today()).order_by('date')[:5]
#     return render(request, 'homepage/home.html', {'featured_matches': featured_matches})

# def match_detail(request, match_id):
#     match = get_object_or_404(Match, id=match_id)
#     return render(request, 'homepage/match_detail.html', {'match': match})
