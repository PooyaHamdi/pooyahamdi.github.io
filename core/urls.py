from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("research/", views.research, name="research"),
    path("publications/", views.publications, name="publications"),
    path("team/", views.team, name="team"),
]
