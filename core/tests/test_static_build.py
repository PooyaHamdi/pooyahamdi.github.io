import json
import tempfile
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase, override_settings

from core.models import Profile


class StaticBuildTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_site")

    def test_build_writes_pages_with_base_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            call_command("build_site", output=tmp, base_path="pooya-hamdi", stdout=open("/dev/null", "w"))
            out = Path(tmp)
            for page in ["index.html", "research/index.html", "publications/index.html", "team/index.html"]:
                self.assertTrue((out / page).exists(), page)
            home = (out / "index.html").read_text()
            self.assertIn('href="/pooya-hamdi/research/"', home)
            self.assertIn('href="/pooya-hamdi/static/core/site.css"', home)
            self.assertNotIn("/admin", home)
            self.assertTrue((out / "static/core/site.css").exists())

    def test_save_exports_content_when_enabled(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "site.json"
            with override_settings(CONTENT_AUTOEXPORT=True, CONTENT_FILE=target):
                p = Profile.load()
                p.tagline = "exported tagline"
                p.save()
            data = json.loads(target.read_text())
            profile = next(o for o in data if o["model"] == "core.profile")
            self.assertEqual(profile["fields"]["tagline"], "exported tagline")
