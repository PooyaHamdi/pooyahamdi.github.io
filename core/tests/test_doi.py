from unittest import mock

from django.test import TestCase

from core import doi
from core.models import Publication

TITLE = "Damage characterization during laboratory strength testing: a 3D-finite-discrete element approach"


def crossref(*items, status=200):
    return mock.Mock(status_code=status, headers={}, json=lambda: {"message": {"items": list(items)}},
                     raise_for_status=mock.Mock())


def item(doi_, title, year):
    return {"DOI": doi_, "title": [title], "issued": {"date-parts": [[year]]}}


class MatchTests(TestCase):
    def test_accepts_same_title_ignoring_case_and_punctuation(self):
        items = [item("10.1/x", "Damage Characterization During Laboratory Strength Testing: A 3D-Finite-Discrete Element Approach", 2014)]
        self.assertEqual(doi.best_match(TITLE, 2014, items), "10.1/x")

    def test_rejects_different_title(self):
        items = [item("10.1/y", "Strength and damage of nanoplatelets reinforced polymer", 2014)]
        self.assertIsNone(doi.best_match(TITLE, 2014, items))

    def test_rejects_same_title_from_a_different_year(self):
        self.assertIsNone(doi.best_match(TITLE, 2014, [item("10.1/z", TITLE, 2019)]))


class LinkTests(TestCase):
    def test_replaces_scholar_links_and_keeps_manual_ones(self):
        scholar_pub = Publication.objects.create(title=TITLE, year=2014, url="https://scholar.google.com/citations?x")
        manual_pub = Publication.objects.create(title="Hand edited", url="https://example.org/paper")
        session = mock.Mock()
        session.get.return_value = crossref(item("10.1016/j.compgeo.2014.03.011", TITLE, 2014))

        linked, not_found = doi.link_publications(Publication.objects.all(), session=session, pause=0)

        scholar_pub.refresh_from_db()
        manual_pub.refresh_from_db()
        self.assertEqual(scholar_pub.url, "https://doi.org/10.1016/j.compgeo.2014.03.011")
        self.assertEqual(manual_pub.url, "https://example.org/paper")
        self.assertEqual((len(linked), len(not_found)), (1, 0))
        self.assertEqual(session.get.call_count, 1)

    def test_no_match_keeps_scholar_link(self):
        pub = Publication.objects.create(title=TITLE, year=2014, url="https://scholar.google.com/citations?x")
        session = mock.Mock()
        session.get.return_value = crossref()
        doi.link_publications([pub], session=session, pause=0)
        pub.refresh_from_db()
        self.assertIn("scholar.google.com", pub.url)

    @mock.patch("core.doi.time.sleep")
    def test_retries_after_rate_limit(self, sleep):
        session = mock.Mock()
        session.get.side_effect = [crossref(status=429), crossref(item("10.1/x", TITLE, 2014))]
        self.assertEqual(doi.lookup_doi(TITLE, 2014, session=session), "10.1/x")
        sleep.assert_called_once()
