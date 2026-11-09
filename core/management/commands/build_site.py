import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.test import Client
from django.test.utils import override_settings
from django.urls import get_script_prefix, reverse, set_script_prefix

from core.models import Project

PAGES = ["home", "research", "publications"]  # "team" hidden for now


class Command(BaseCommand):
    help = "Render the public pages to static HTML for GitHub Pages."

    def add_arguments(self, parser):
        parser.add_argument("--output", default="_site", help="Output directory (default: _site)")
        parser.add_argument(
            "--base-path",
            default="/",
            help="URL path the site is served under, e.g. /pooya-hamdi/ for a GitHub project page.",
        )

    def handle(self, *args, output, base_path, **options):
        out = Path(output).resolve()
        base_path = "/" + base_path.strip("/") + "/" if base_path.strip("/") else "/"

        # Before any request sets a script prefix.
        paths = [reverse(name) for name in PAGES] + [p.get_absolute_url() for p in Project.objects.all()]

        if out.exists():
            shutil.rmtree(out)
        out.mkdir(parents=True)

        # The script prefix makes {% url %}, {% static %} and file .url values
        # include the base path, so links work under /<repo>/ on GitHub Pages.
        # Overriding STORAGES also resets the storage objects so they pick it up.
        old_prefix = get_script_prefix()
        set_script_prefix(base_path)
        with override_settings(
            DEBUG=False,
            ALLOWED_HOSTS=["localhost"],
            MIDDLEWARE=[m for m in settings.MIDDLEWARE if "whitenoise" not in m],
            STORAGES={**settings.STORAGES, "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}},
        ):
            client = Client(HTTP_HOST="localhost")
            for path in paths:
                response = client.get(path)
                if response.status_code != 200:
                    raise CommandError(f"{path} returned {response.status_code}")
                target = out / path.lstrip("/") / "index.html"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(response.content)
                self.stdout.write(f"  {path} -> {target.relative_to(out)}")
        set_script_prefix(old_prefix)

        shutil.copytree(Path(settings.BASE_DIR) / "core" / "static", out / "static")
        if Path(settings.MEDIA_ROOT).exists():
            shutil.copytree(settings.MEDIA_ROOT, out / "media")
        (out / ".nojekyll").touch()

        self.stdout.write(self.style.SUCCESS(f"Built site in {out} (base path {base_path})"))
