"""Link publications to the article itself via its DOI.

Google Scholar does not let automated clients open a paper's own page, so the
article link can't be taken from Scholar. Instead, each title is looked up in
Crossref (the public DOI registry) and the publication links to
https://doi.org/<doi>, which opens the publisher's page.

Only links that still point to Google Scholar (or are empty) are replaced, so
a link edited by hand in the admin is kept. A failed lookup leaves the link as
it was.
"""
import logging
import re
import time
from difflib import SequenceMatcher

import requests

logger = logging.getLogger(__name__)

CROSSREF_URL = "https://api.crossref.org/works"
USER_AGENT = "PersonalAcademicSite/1.0 (links publications on the author's own website)"
MIN_TITLE_SIMILARITY = 0.9
PAUSE_SECONDS = 1.0
RETRIES = 3


def _normalize(title):
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def _year(item):
    for key in ("issued", "published-print", "published-online"):
        parts = (item.get(key) or {}).get("date-parts") or [[None]]
        if parts[0] and parts[0][0]:
            return parts[0][0]
    return None


def best_match(title, year, items):
    """Return the DOI of the Crossref item that clearly is this publication, or None."""
    wanted = _normalize(title)
    best, best_score = None, 0.0
    for item in items:
        for candidate in item.get("title") or []:
            score = SequenceMatcher(None, wanted, _normalize(candidate)).ratio()
            if score < MIN_TITLE_SIMILARITY:
                continue
            found_year = _year(item)
            if year and found_year and abs(found_year - year) > 1:
                continue
            if score > best_score:
                best, best_score = item.get("DOI"), score
    return best


def lookup_doi(title, year=None, session=None):
    session = session or requests.Session()
    params = {"query.bibliographic": title, "rows": 5, "select": "DOI,title,issued,published-print,published-online"}
    for attempt in range(RETRIES):
        try:
            resp = session.get(CROSSREF_URL, params=params, headers={"User-Agent": USER_AGENT}, timeout=20)
            if resp.status_code == 429 and attempt < RETRIES - 1:
                # Crossref asks clients to slow down; wait as long as it says.
                time.sleep(_retry_after(resp))
                continue
            resp.raise_for_status()
            items = resp.json()["message"]["items"]
        except (requests.RequestException, ValueError, KeyError) as exc:
            logger.warning("Crossref lookup failed for %r: %s", title, exc)
            return None
        return best_match(title, year, items)
    return None


def _retry_after(resp, default=5.0):
    try:
        return min(float(resp.headers.get("Retry-After", default)), 60.0)
    except ValueError:
        return default


def needs_link(pub):
    return not pub.url or "scholar.google." in pub.url


def link_publications(publications, session=None, pause=PAUSE_SECONDS):
    """Point each publication that still links to Scholar at its DOI. Returns (linked, not_found)."""
    session = session or requests.Session()
    linked, not_found = [], []
    for pub in publications:
        if not needs_link(pub):
            continue
        doi = lookup_doi(pub.title, pub.year, session=session)
        if doi:
            pub.url = f"https://doi.org/{doi}"
            pub.save(update_fields=["url"])
            linked.append(pub)
        else:
            not_found.append(pub)
        if pause:
            time.sleep(pause)
    return linked, not_found
