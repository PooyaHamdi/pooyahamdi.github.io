from pathlib import Path
from unittest import mock

from django.core.management import call_command
from django.test import TestCase

from core import scholar
from core.models import Publication, ScholarStats

FIXTURE = (Path(__file__).parent / "fixtures" / "scholar_profile.html").read_text()


class ParseTests(TestCase):
    def test_stats(self):
        p = scholar.parse_profile_html(FIXTURE)
        self.assertEqual((p.citations, p.citations_recent), (1575, 418))
        self.assertEqual((p.h_index, p.h_index_recent), (12, 11))
        self.assertEqual((p.i10_index, p.i10_index_recent), (14, 11))
        self.assertEqual(p.recent_since, 2021)

    def test_yearly_handles_missing_bars(self):
        p = scholar.parse_profile_html(FIXTURE)
        self.assertEqual(p.citations_per_year, {"2023": 64, "2024": 0, "2025": 82, "2026": 118})

    def test_publications(self):
        pubs = scholar.parse_profile_html(FIXTURE).publications
        self.assertEqual(len(pubs), 2)
        first = pubs[0]
        self.assertTrue(first.title.startswith("Damage characterization"))
        self.assertEqual(first.authors, "P Hamdi, D Stead, D Elmo")
        self.assertEqual(first.venue, "Computers and Geotechnics 60, 33-46")
        self.assertEqual((first.year, first.citations), (2014, 81))
        self.assertEqual(first.scholar_id, "QqegjnAAAAAJ:u5HHmVD_uO8C")
        self.assertEqual(pubs[1].citations, 0)

    def test_blocked_page_raises(self):
        with self.assertRaises(scholar.ScholarError):
            scholar.parse_profile_html("<html><body>Please show you're not a robot</body></html>")


class SyncTests(TestCase):
    def _response(self, status=200, text=FIXTURE):
        return mock.Mock(status_code=status, text=text)

    def test_sync_updates_and_preserves_manual_fields(self):
        Publication.objects.create(
            title="Damage characterization during laboratory strength testing: a 3D-finite-discrete element approach",
            citations=10, venue="Edited by hand",
        )
        session = mock.Mock(headers={})
        session.get.return_value = self._response()
        stats, created, updated = scholar.save_profile(scholar.fetch_profile("x", session=session))
        self.assertEqual((created, updated), (1, 1))
        self.assertEqual(stats.citations, 1575)
        pub = Publication.objects.get(title__startswith="Damage")
        self.assertEqual(pub.citations, 81)
        self.assertEqual(pub.venue, "Edited by hand")
        self.assertNotIn("Mozilla", session.headers["User-Agent"])

    def test_failed_fetch_keeps_existing_data(self):
        call_command("seed_site")
        with mock.patch("core.scholar.requests.Session") as Session:
            Session.return_value = mock.Mock(headers={})
            Session.return_value.get.return_value = self._response(status=429, text="")
            with self.assertRaises(scholar.ScholarError):
                scholar.sync()
        self.assertEqual(ScholarStats.load().citations, 575)
