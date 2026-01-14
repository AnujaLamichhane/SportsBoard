from django.apps import AppConfig


class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'

    def ready(self):
        # Run only once (avoid duplicate scheduler in dev server reload)
        if not hasattr(self, 'scheduler_started'):
            self.scheduler_started = True

            from apscheduler.schedulers.background import BackgroundScheduler
            from .rss_fetcher import fetch_news

            scheduler = BackgroundScheduler()
            # Run fetch_news every 30 minutes
            scheduler.add_job(fetch_news, 'interval', minutes=30, id='fetch_news_job')
            scheduler.start()


            # install apschedular and feedparser