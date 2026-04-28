import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Creates a superuser if none exists, with verified email'

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.environ.get('SUPERUSER_USERNAME', 'admin')
        email = os.environ.get('SUPERUSER_EMAIL', 'admin@sportsboard.com')
        password = os.environ.get('SUPERUSER_PASSWORD', 'changeme123')

        # Get or create the superuser
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'is_staff': True,
                'is_superuser': True,
            }
        )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Superuser {username} created.'))
        else:
            self.stdout.write(f'Superuser {username} already exists — ensuring email is verified.')

        # Force verify the email in allauth regardless of whether
        # user was just created or already existed
        try:
            from allauth.account.models import EmailAddress
            EmailAddress.objects.update_or_create(
                user=user,
                email=email,
                defaults={
                    'primary': True,
                    'verified': True,
                }
            )
            self.stdout.write(
                self.style.SUCCESS(f'Email {email} marked as verified.')
            )
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Could not verify email: {e}')
            )