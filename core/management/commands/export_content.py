from django.conf import settings
from django.core.management.base import BaseCommand

from core.content import export_content


class Command(BaseCommand):
    help = "Write all site content to content/site.json (normally done automatically on every admin save)."

    def handle(self, *args, **options):
        export_content()
        self.stdout.write(self.style.SUCCESS(f"Wrote {settings.CONTENT_FILE}"))
