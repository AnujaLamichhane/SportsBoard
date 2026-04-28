import os
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Sets up the Django sites framework domain'

    def handle(self, *args, **options):
        # Import here to avoid AppRegistryNotReady errors
        from django.contrib.sites.models import Site

        domain = os.environ.get('SITE_DOMAIN', 'sportsboard.onrender.com')
        site_id = int(os.environ.get('SITE_ID', '1'))

        Site.objects.update_or_create(
            id=site_id,
            defaults={
                'domain': domain,
                'name': 'SportsBoard'
            }
        )
        self.stdout.write(
            self.style.SUCCESS(f'Site domain set to: {domain}')
        )