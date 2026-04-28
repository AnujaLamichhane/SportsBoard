import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Creates a superuser if none exists'

    def handle(self, *args, **options):
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username=os.environ.get('SUPERUSER_USERNAME', 'admin'),
                email=os.environ.get('SUPERUSER_EMAIL', 'admin@sportsboard.com'),
                password=os.environ.get('SUPERUSER_PASSWORD', 'changeme123')
            )
            self.stdout.write(self.style.SUCCESS('Superuser created successfully.'))
        else:
            self.stdout.write('Superuser already exists — skipping.')