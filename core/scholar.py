"""Fetch and parse a public Google Scholar profile page.

Scholar has no official API. This module makes a plain, identified request for
one public profile and parses the HTML. If Scholar refuses (captcha, 429, layout
change), sync fails cleanly and the existing data in the database is kept.
"""
import logging
import re
from dataclasses import dataclass, field

import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)

PROFILE_URL = "https://scholar.google.com/citations"
USER_AGENT = "PersonalAcademicSite/1.0 (citation refresh for the profile owner's own website)"
PAGE_SIZE = 100
MAX_PAGES = 5


class ScholarError(Exception):
    pass


@dataclass
class ParsedPublication:
    title: str
    authors: str
    venue: str
    year: int | None
    citations: int
    url: str
    scholar_id: str


@dataclass
class ParsedProfile:
    citations: int = 0
    citations_recent: int = 0
    h_index: int = 0
    h_index_recent: int = 0
    i10_index: int = 0
    i10_index_recent: int = 0
    recent_since: int | None = None
    citations_per_year: dict = field(default_factory=dict)
    publications: list = field(default_factory=list)


def _int(text):
    digits = re.sub(r"[^\d]", "", text or "")
    return int(digits) if digits else 0


def parse_profile_html(html):
    """Parse stats, yearly citations and publications from one profile page."""
    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one("#gsc_rsb_st")
    if table is None:
        raise ScholarError("Citation table not found (blocked, or Scholar changed its layout).")

    profile = ParsedProfile()

    header = table.select("thead th")
    if len(header) >= 3:
        match = re.search(r"(\d{4})", header[2].get_text())
        profile.recent_since = int(match.group(1)) if match else None

    rows = {}
    for tr in table.select("tbody tr"):
        label = tr.select_one(".gsc_rsb_sc1")
        values = [_int(td.get_text()) for td in tr.select(".gsc_rsb_std")]
        if label and len(values) >= 2:
            rows[label.get_text(strip=True).lower()] = values
    profile.citations, profile.citations_recent = rows.get("citations", [0, 0])[:2]
    profile.h_index, profile.h_index_recent = rows.get("h-index", [0, 0])[:2]
    profile.i10_index, profile.i10_index_recent = rows.get("i10-index", [0, 0])[:2]

    years = [_int(el.get_text()) for el in soup.select(".gsc_g_t")]
    # Bars are positioned by z-index; years with zero citations have no bar.
    bars = {}
    for bar in soup.select(".gsc_g_a"):
        match = re.search(r"z-index:\s*(\d+)", bar.get("style", ""))
        count = bar.select_one(".gsc_g_al")
        if match and count:
            bars[int(match.group(1))] = _int(count.get_text())
    for i, year in enumerate(years):
        z = len(years) - i
        profile.citations_per_year[str(year)] = bars.get(z, 0)

    profile.publications = parse_publication_rows(soup)
    return profile


def parse_publication_rows(soup):
    pubs = []
    for row in soup.select("tr.gsc_a_tr"):
        link = row.select_one("a.gsc_a_at")
        if link is None:
            continue
        grey = row.select(".gs_gray")
        venue = grey[1].get_text(" ", strip=True) if len(grey) > 1 else ""
        venue = re.sub(r",\s*\d{4}$", "", venue).strip()
        href = link.get("href", "")
        match = re.search(r"citation_for_view=([^&]+)", href)
        year_el = row.select_one(".gsc_a_y")
        cites_el = row.select_one(".gsc_a_c a")
        pubs.append(
            ParsedPublication(
                title=link.get_text(strip=True),
                authors=grey[0].get_text(strip=True) if grey else "",
                venue=venue,
                year=_int(year_el.get_text()) or None if year_el else None,
                citations=_int(cites_el.get_text()) if cites_el else 0,
                url=f"https://scholar.google.com{href}" if href.startswith("/") else href,
                scholar_id=match.group(1) if match else "",
            )
        )
    return pubs


def fetch_profile(user_id=None, session=None):
    user_id = user_id or settings.SCHOLAR_USER_ID
    session = session or requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    profile = None
    for page in range(MAX_PAGES):
        params = {"user": user_id, "hl": "en", "cstart": page * PAGE_SIZE, "pagesize": PAGE_SIZE}
        try:
            resp = session.get(PROFILE_URL, params=params, timeout=20)
        except requests.RequestException as exc:
            raise ScholarError(f"Could not reach Google Scholar: {exc}") from exc
        if resp.status_code != 200:
            raise ScholarError(f"Google Scholar returned HTTP {resp.status_code}.")
        if profile is None:
            profile = parse_profile_html(resp.text)
            new = profile.publications
        else:
            new = parse_publication_rows(BeautifulSoup(resp.text, "html.parser"))
            profile.publications.extend(new)
        if len(new) < PAGE_SIZE:
            break
    return profile


@transaction.atomic
def save_profile(parsed):
    from .models import Publication, ScholarStats

    stats = ScholarStats.load()
    for name in ("citations", "citations_recent", "h_index", "h_index_recent", "i10_index",
                 "i10_index_recent", "recent_since", "citations_per_year"):
        setattr(stats, name, getattr(parsed, name))
    stats.last_updated = timezone.now()
    stats.save()

    created = updated = 0
    for pub in parsed.publications:
        existing = None
        if pub.scholar_id:
            existing = Publication.objects.filter(scholar_id=pub.scholar_id).first()
        if existing is None:
            existing = Publication.objects.filter(title__iexact=pub.title).first()
        if existing is None:
            Publication.objects.create(**pub.__dict__)
            created += 1
        else:
            # Only refresh what Scholar owns; keep manual edits to title, authors and venue.
            existing.citations = pub.citations
            existing.scholar_id = pub.scholar_id or existing.scholar_id
            existing.year = existing.year or pub.year
            existing.url = existing.url or pub.url
            existing.save()
            updated += 1
    return stats, created, updated


def sync(user_id=None):
    """Fetch and store. Raises ScholarError and leaves the DB untouched on failure.

    Afterwards, publications still linking to Scholar are pointed at their DOI
    (see core/doi.py). That step never fails the sync.
    """
    from . import doi
    from .models import Publication

    result = save_profile(fetch_profile(user_id))
    doi.link_publications(Publication.objects.all())
    return result
