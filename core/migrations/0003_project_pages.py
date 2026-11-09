from django.db import migrations, models
import django.db.models.deletion
from django.utils.text import slugify


def fill_slugs(apps, schema_editor):
    Project = apps.get_model("core", "Project")
    used = set()
    for p in Project.objects.order_by("pk"):
        base = slugify(p.title)[:80].rstrip("-") or "project"
        slug, n = base, 2
        while slug in used:
            suffix = f"-{n}"
            slug = base[: 80 - len(suffix)] + suffix
            n += 1
        used.add(slug)
        # update() sends no save signal, so the content export doesn't run mid-migration.
        Project.objects.filter(pk=p.pk).update(slug=slug)


class Migration(migrations.Migration):
    dependencies = [("core", "0002_experience_profile_institution_url_and_more")]

    operations = [
        migrations.AddField(
            model_name="project",
            name="slug",
            field=models.SlugField(max_length=80, null=True),
        ),
        migrations.RunPython(fill_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="project",
            name="slug",
            field=models.SlugField(
                max_length=80, unique=True,
                help_text="The project page's web address: /research/<slug>/. Filled in from the title.",
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="partners",
            field=models.CharField(blank=True, max_length=500, verbose_name="Partners / collaborators"),
        ),
        migrations.AddField(
            model_name="project",
            name="body",
            field=models.TextField(
                blank=True, verbose_name="Full description",
                help_text="Shown on the project's own page. Separate paragraphs with a blank line. "
                          "Formatting: <code>## Heading</code>, <code>- list item</code>, <code>**bold**</code>, "
                          "<code>[link text](https://...)</code>.",
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="summary",
            field=models.TextField(blank=True, help_text="Short text shown on the Research page card."),
        ),
        migrations.AlterField(
            model_name="project",
            name="link",
            field=models.URLField(
                blank=True, max_length=500, verbose_name="Original source page",
                help_text="For your reference only (e.g. the old RWTH page). Not shown on the site.",
            ),
        ),
        migrations.CreateModel(
            name="ProjectImage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("image", models.ImageField(upload_to="projects/")),
                ("caption", models.CharField(blank=True, max_length=500)),
                ("credit", models.CharField(blank=True, help_text="e.g. © LIH", max_length=200)),
                ("order", models.PositiveIntegerField(default=0, help_text="Lower numbers appear first.")),
                ("project", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="images", to="core.project")),
            ],
            options={"ordering": ["order", "pk"], "verbose_name": "Photo"},
        ),
    ]
