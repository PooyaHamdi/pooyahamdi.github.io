from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import path, reverse

from . import scholar
from .models import Education, Experience, Profile, Project, Publication, ScholarStats, Student


class SingletonAdmin(admin.ModelAdmin):
    """Skip the list view and go straight to editing the single row."""

    def has_add_permission(self, request):
        return not self.model.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = self.model.load()
        return redirect(reverse(f"admin:core_{self.model._meta.model_name}_change", args=[obj.pk]))


@admin.register(Profile)
class ProfileAdmin(SingletonAdmin):
    fieldsets = [
        (None, {"fields": ["name", "title", "affiliation", "tagline", "photo"]}),
        ("About", {"fields": ["bio", "research_interests"]}),
        ("Links", {"fields": ["email", "linkedin_url", "scholar_url", "institution_url", "orcid_url", "cv"]}),
        ("Team page", {"fields": ["supervision_summary"]}),
    ]


@admin.register(ScholarStats)
class ScholarStatsAdmin(SingletonAdmin):
    change_form_template = "admin/core/scholarstats/change_form.html"
    readonly_fields = ["last_updated"]
    fields = [
        ("citations", "citations_recent"),
        ("h_index", "h_index_recent"),
        ("i10_index", "i10_index_recent"),
        "recent_since",
        "citations_per_year",
        "last_updated",
    ]

    def get_urls(self):
        custom = [path("refresh/", self.admin_site.admin_view(self.refresh_view), name="core_scholarstats_refresh")]
        return custom + super().get_urls()

    def refresh_view(self, request):
        if request.method == "POST":
            try:
                stats, created, updated = scholar.sync()
            except scholar.ScholarError as exc:
                self.message_user(request, f"Could not refresh from Google Scholar: {exc} Existing numbers were kept.", messages.ERROR)
            else:
                self.message_user(
                    request,
                    f"Refreshed: {stats.citations} citations, h-index {stats.h_index}. "
                    f"{created} new and {updated} updated publications.",
                    messages.SUCCESS,
                )
        return redirect(reverse("admin:core_scholarstats_changelist"))


class OrderedAdmin(admin.ModelAdmin):
    list_editable = ["order"]


@admin.register(Education)
class EducationAdmin(OrderedAdmin):
    list_display = ["degree", "field", "institution", "start_year", "end_year", "order"]


@admin.register(Experience)
class ExperienceAdmin(OrderedAdmin):
    list_display = ["role", "organization", "start_year", "end_year", "order"]


@admin.register(Project)
class ProjectAdmin(OrderedAdmin):
    list_display = ["title", "status", "start_year", "end_year", "order"]
    list_filter = ["status"]


@admin.register(Student)
class StudentAdmin(OrderedAdmin):
    list_display = ["name", "level", "status", "start_year", "order"]
    list_filter = ["status", "level"]


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ["title", "year", "citations", "featured"]
    list_editable = ["featured"]
    list_filter = ["featured", "year"]
    search_fields = ["title", "authors", "venue"]
