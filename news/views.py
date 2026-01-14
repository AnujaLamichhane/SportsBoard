# from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from .models import Article
import feedparser
from datetime import datetime, timezone, timedelta

# def index(request):
#     articles = Article.objects.order_by('-published')[:20]
#     return render(request, 'news/index.html', {'articles': articles})

# def article_detail(request, article_id):
#     article = get_object_or_404(Article, id=article_id)
#     return render(request, 'news/article_detail.html', {'article': article})

FEEDS = [
    "https://ekantipur.com/rss/sports",
    "https://www.hamrokhelkud.com/feed/",
    "https://kathmandupost.com/rss/sports",
]

def index(request):
    articles = []
    for url in FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:  # fetch top 10 news per source
            published = None
            if hasattr(entry, "published_parsed"):
                published = datetime(*entry.published_parsed[:6])
                published = published + timedelta(hours=5, minutes=45)
            
            articles.append({
                "title": entry.title,
                "summary": getattr(entry, "summary", "")[:200],
                "link": entry.link,
                "source": url.split("//")[1].split("/")[0],
                "published": published
            })

    # Sort articles by published date (newest first)
    articles = sorted(articles, key=lambda x: x["published"] or datetime.min, reverse=True)

    return render(request, "news/index.html", {"articles": articles})