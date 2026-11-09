from django.shortcuts import get_object_or_404, render

from .models import Education, Experience, Project, Publication, ScholarStats, Student

CHART_WIDTH = 640
CHART_HEIGHT = 150


def _citation_bars(stats):
    """Pre-compute SVG geometry for the citations-per-year bar chart.

    Text (axis years, value label, tooltip) is positioned in HTML using the
    `left`/`top` percentages so it stays readable at any chart width.
    """
    yearly = stats.yearly
    if not yearly:
        return []
    peak = max(c for _, c in yearly) or 1
    n = len(yearly)
    slot = CHART_WIDTH / n
    bar_width = slot * 0.62
    base = CHART_HEIGHT
    bars = []
    for i, (year, count) in enumerate(yearly):
        h = CHART_HEIGHT * count / peak
        x = i * slot + (slot - bar_width) / 2
        y = base - h
        r = min(4, h, bar_width / 2)  # 4px rounded data-end, square at the baseline
        path = (
            f"M{x:.1f},{base:.1f} V{y + r:.1f} Q{x:.1f},{y:.1f} {x + r:.1f},{y:.1f} "
            f"H{x + bar_width - r:.1f} Q{x + bar_width:.1f},{y:.1f} {x + bar_width:.1f},{y + r:.1f} V{base:.1f} Z"
        ) if count else ""
        from_end = n - 1 - i
        bars.append({
            "year": year,
            "count": count,
            "path": path,
            "slot_x": round(i * slot, 1),
            "slot_w": round(slot, 1),
            "left": round((x + bar_width / 2) / CHART_WIDTH * 100, 2),
            "top": round(y / CHART_HEIGHT * 100, 2),
            "label_year": from_end % 2 == 0,  # every other year, always the latest
            "label_mobile": from_end % 4 == 0,
        })
    return bars


def home(request):
    stats = ScholarStats.load()
    return render(request, "core/home.html", {
        "stats": stats,
        "bars": _citation_bars(stats),
        "chart": {"w": CHART_WIDTH, "h": CHART_HEIGHT},
        "education": Education.objects.all(),
        "experience": Experience.objects.all(),
        "nav": "about",
    })


def research(request):
    projects = Project.objects.all()
    return render(request, "core/research.html", {
        "ongoing": projects.filter(status=Project.ONGOING),
        "completed": projects.filter(status=Project.COMPLETED),
        "nav": "research",
    })


def project(request, slug):
    return render(request, "core/project.html", {
        "p": get_object_or_404(Project, slug=slug),
        "nav": "research",
    })


def publications(request):
    return render(request, "core/publications.html", {
        "publications": Publication.objects.all(),
        "stats": ScholarStats.load(),
        "nav": "publications",
    })


def team(request):
    students = Student.objects.all()
    return render(request, "core/team.html", {
        "current": students.filter(status=Student.CURRENT),
        "alumni": students.filter(status=Student.ALUMNI),
        "nav": "team",
    })
