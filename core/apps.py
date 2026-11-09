from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "core"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        from . import content, images  # noqa: F401  (connect the auto-export and image-shrinking signals)
