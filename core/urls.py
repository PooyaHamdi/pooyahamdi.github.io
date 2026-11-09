from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("research/", views.research, name="research"),
    path("publications/", views.publications, name="publications"),
    # Team page hidden for now. Re-enable with the nav link in base.html and PAGES in build_site.py.
    # path("team/", views.team, name="team"),
]
