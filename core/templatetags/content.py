import re

import markdown as md
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

EXTERNAL_LINK = re.compile(r'<a href="(https?://[^"]*)"')


@register.filter
def markdown(text):
    """Render the admin's plain-text formatting (headings, lists, bold, links) to HTML.

    Links to other websites open in a new tab.
    """
    html = md.markdown(text or "", extensions=["sane_lists"])
    return mark_safe(EXTERNAL_LINK.sub(r'<a href="\1" target="_blank" rel="noopener"', html))
