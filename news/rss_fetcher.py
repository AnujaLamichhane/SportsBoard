import os
import sys  
# import django
import feedparser
from datetime import datetime
from news.models import Article

# pip install django-apscheduler


# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# --- Django setup ---
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SportsBoard.settings")
# django.setup()
# -------------------


RSS_FEEDS = {
    "Ekantipur": "https://ekantipur.com/rss/sports",
    "Kathmandu Post": "https://kathmandupost.com/rss/sports",
    "HamroKhelkud": "https://www.hamrokhelkud.com/feed/",
}

# def fetch_news():
#     for source, url in RSS_FEEDS.items():
#         feed = feedparser.parse(url)
#         for entry in feed.entries:
#             if not Article.objects.filter(link=entry.link).exists():
#                 published = getattr(entry, 'published', None)
#                 if published:
#                     published = datetime(*entry.published_parsed[:6])
#                 Article.objects.create(
#                     title=entry.title,
#                     summary=getattr(entry, 'summary', ''),
#                     link=entry.link,
#                     source=source,
#                     published=published
#                )
#     print("News fetched successfully!")

# if __name__ == "__main__":
#     fetch_news()

def fetch_news():
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:  # fetch top 5
            # check if this news already exists in DB
            if Article.objects.filter(link=entry.link).exists():
                continue

            published = None
            if hasattr(entry, 'published_parsed'):
                published = datetime(*entry.published_parsed[:6])
            Article.objects.create(
                title=entry.title,
                summary=getattr(entry, 'summary', '')[:200],
                link=entry.link,
                source=url.split("//")[1].split("/")[0],
                published=published,
                is_auto=True
            )
