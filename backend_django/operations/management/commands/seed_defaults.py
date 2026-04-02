import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Create or update the default operational superuser from environment variables."

    def handle(self, *args, **options):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME", "operator")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL", "operator@example.com")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

        if not password:
            self.stdout.write(
                self.style.WARNING("DJANGO_SUPERUSER_PASSWORD belum diset, skip seed user."),
            )
            return

        User = get_user_model()
        user, created = User.objects.update_or_create(
            username=username,
            defaults={
                "email": email,
                "last_login": timezone.now(),
                "is_staff": True,
                "is_superuser": True,
            },
        )
        user.email = email
        user.set_password(password)
        user.save()

        action = "dibuat" if created else "diupdate"
        self.stdout.write(self.style.SUCCESS(f"User default {action}: {username}"))
