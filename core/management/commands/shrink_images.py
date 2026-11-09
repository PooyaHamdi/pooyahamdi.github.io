from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from core.images import shrink


class Command(BaseCommand):
    help = "Shrink oversized photos already in media/, in place (file names stay the same)."

    def handle(self, *args, **options):
        for path in sorted(Path(settings.MEDIA_ROOT).rglob("*")):
            if path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
                continue
            before = path.stat().st_size
            smaller = shrink(path.read_bytes())
            if smaller is None:
                self.stdout.write(f"  {path.relative_to(settings.MEDIA_ROOT)}: already small")
                continue
            path.write_bytes(smaller)
            self.stdout.write(f"  {path.relative_to(settings.MEDIA_ROOT)}: {before // 1024} KB -> {len(smaller) // 1024} KB")
