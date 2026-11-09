from .models import Profile


def site_profile(request):
    return {"profile": Profile.load()}
