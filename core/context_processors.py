from django.conf import settings

from .models import Profile

CSS_FILE = settings.BASE_DIR / "core" / "static" / "core" / "site.css"


def site_profile(request):
    return {
        "profile": Profile.load(),
        # Changes whenever site.css changes, so browsers fetch the new file instead of a cached copy.
        "css_version": int(CSS_FILE.stat().st_mtime),
    }
