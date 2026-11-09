from django.core.management.base import BaseCommand, CommandError

from core import scholar


class Command(BaseCommand):
    help = "Refresh citation statistics and publications from Google Scholar."

    def add_arguments(self, parser):
        parser.add_argument("--user", help="Scholar user id (defaults to settings.SCHOLAR_USER_ID)")

    def handle(self, *args, **opts):
        try:
            stats, created, updated = scholar.sync(opts.get("user"))
        except scholar.ScholarError as exc:
            raise CommandError(f"{exc} Existing data was kept.")
        self.stdout.write(self.style.SUCCESS(
            f"{stats.citations} citations, h-index {stats.h_index}, i10-index {stats.i10_index}; "
            f"{created} new / {updated} updated publications."
        ))
