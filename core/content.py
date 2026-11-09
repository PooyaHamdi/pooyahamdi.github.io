"""Keep content/site.json in sync with the database.

The JSON file is what gets committed to git and what the GitHub Action builds
the static site from. Every save or delete of a core model (from the admin,
seed_site, or update_scholar) rewrites the file, so there is no separate
export step to remember.
"""
from django.apps import apps
from django.conf import settings
from django.core.management import call_command
from django.db.models.signals import post_delete, post_save


def export_content():
    path = settings.CONTENT_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    call_command("dumpdata", "core", indent=2, output=str(path), verbosity=0)


def _on_change(sender, raw=False, **kwargs):
    if raw or not settings.CONTENT_AUTOEXPORT:
        return
    if sender._meta.app_label == "core":
        export_content()


post_save.connect(_on_change, dispatch_uid="core-content-save")
post_delete.connect(_on_change, dispatch_uid="core-content-delete")
