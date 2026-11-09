from unittest import skip

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from core.models import Profile, Student


class PageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_site")

    def test_home(self):
        r = self.client.get(reverse("home"))
        self.assertContains(r, "Dr. Pooya Hamdi")
        self.assertContains(r, "575")
        self.assertContains(r, "Education")
        self.assertContains(r, 'class="mark"')
        self.assertContains(r, "Google Scholar")

    def test_home_shows_rwth_profile_and_career(self):
        r = self.client.get(reverse("home"))
        self.assertContains(r, ">RWTH profile</a>")
        self.assertContains(r, "Career")
        self.assertContains(r, "Golder Associates Ltd.")
        self.assertContains(r, "Simon Fraser University")

    def test_research(self):
        r = self.client.get(reverse("research"))
        self.assertContains(r, "Current projects")
        self.assertContains(r, "Completed projects")

    def test_publications(self):
        r = self.client.get(reverse("publications"))
        self.assertContains(r, "Damage characterization")
        self.assertContains(r, "Cited by 125")

    @skip("Team page hidden for now")
    def test_team(self):
        r = self.client.get(reverse("team"))
        self.assertContains(r, "Current students")
        self.assertContains(r, "Alumni")
        self.assertContains(r, "Over 15 MSc and BSc theses")

    def test_linkedin_link_appears_once_set(self):
        p = Profile.load()
        p.linkedin_url = "https://www.linkedin.com/in/example"
        p.save()
        self.assertContains(self.client.get(reverse("home")), "linkedin.com/in/example")

    def test_seed_is_idempotent(self):
        call_command("seed_site")
        self.assertEqual(Student.objects.count(), 4)


class AdminTests(TestCase):
    def setUp(self):
        call_command("seed_site")
        User.objects.create_superuser("admin", "a@example.com", "pw")
        self.client.login(username="admin", password="pw")

    def test_admin_pages_load(self):
        for name in ["education", "project", "student", "publication"]:
            self.assertEqual(self.client.get(reverse(f"admin:core_{name}_changelist")).status_code, 200)

    def test_singletons_redirect_to_edit(self):
        r = self.client.get(reverse("admin:core_profile_changelist"))
        self.assertRedirects(r, reverse("admin:core_profile_change", args=[1]))
        r = self.client.get(reverse("admin:core_scholarstats_changelist"), follow=True)
        self.assertContains(r, "Refresh citations from Google Scholar")
