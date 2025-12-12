# from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from .models import Article

def index(request):
    articles = Article.objects.order_by('-published')[:20]
    return render(request, 'news/index.html', {'articles': articles})

def article_detail(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    return render(request, 'news/article_detail.html', {'article': article})
