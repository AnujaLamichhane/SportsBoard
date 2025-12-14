import os
import sys  
import django
import feedparser
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# --- Django setup ---
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SportsBoard.settings")
django.setup()
# -------------------
from news.models import Article

RSS_FEEDS = {
    "Ekantipur": "https://ekantipur.com/rss/sports",
    "Kathmandu Post": "https://kathmandupost.com/rss/sports",
    "HamroKhelkud": "https://www.hamrokhelkud.com/feed/",
}

def fetch_news():
    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if not Article.objects.filter(link=entry.link).exists():
                published = getattr(entry, 'published', None)
                if published:
                    published = datetime(*entry.published_parsed[:6])
                Article.objects.create(
                    title=entry.title,
                    summary=getattr(entry, 'summary', ''),
                    link=entry.link,
                    source=source,
                    published=published
               )
    print("News fetched successfully!")

if __name__ == "__main__":
    fetch_news()
