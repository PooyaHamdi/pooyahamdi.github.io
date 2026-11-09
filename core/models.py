from django.db import models


class SingletonModel(models.Model):
    """A model with exactly one row (pk=1)."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Profile(SingletonModel):
    name = models.CharField(max_length=200)
    title = models.CharField(max_length=200, blank=True, help_text="e.g. Senior Scientist")
    affiliation = models.CharField(max_length=300, blank=True)
    tagline = models.CharField(max_length=300, blank=True, help_text="One line shown under your name.")
    bio = models.TextField(blank=True, help_text="Separate paragraphs with a blank line.")
    research_interests = models.CharField(max_length=500, blank=True, help_text="Comma-separated.")
    photo = models.ImageField(upload_to="profile/", blank=True)
    email = models.EmailField(blank=True)
    linkedin_url = models.URLField("LinkedIn URL", blank=True)
    scholar_url = models.URLField("Google Scholar URL", blank=True)
    orcid_url = models.URLField("ORCID URL", blank=True)
    institution_url = models.URLField("University profile URL", max_length=500, blank=True)
    cv = models.FileField("CV (PDF)", upload_to="cv/", blank=True)
    supervision_summary = models.CharField(max_length=300, blank=True, help_text="Shown at the top of the Team page.")

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profile"

    def __str__(self):
        return self.name or "Profile"

    @property
    def interests_list(self):
        return [i.strip() for i in self.research_interests.split(",") if i.strip()]


class ScholarStats(SingletonModel):
    citations = models.PositiveIntegerField(default=0)
    citations_recent = models.PositiveIntegerField(default=0)
    h_index = models.PositiveIntegerField(default=0)
    h_index_recent = models.PositiveIntegerField(default=0)
    i10_index = models.PositiveIntegerField(default=0)
    i10_index_recent = models.PositiveIntegerField(default=0)
    recent_since = models.PositiveIntegerField(null=True, blank=True, help_text="The 'since' year Scholar uses.")
    citations_per_year = models.JSONField(default=dict, blank=True, help_text='e.g. {"2024": 69, "2025": 82}')
    last_updated = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Citation statistics"
        verbose_name_plural = "Citation statistics"

    def __str__(self):
        return f"{self.citations} citations"

    @property
    def yearly(self):
        """[(year, count)] sorted by year."""
        return sorted(((int(y), int(c)) for y, c in self.citations_per_year.items()), key=lambda t: t[0])


class Education(models.Model):
    degree = models.CharField(max_length=100, help_text="e.g. PhD, MSc, BSc")
    field = models.CharField(max_length=200, blank=True)
    institution = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    start_year = models.PositiveIntegerField(null=True, blank=True)
    end_year = models.PositiveIntegerField(null=True, blank=True)
    thesis = models.CharField("Thesis title", max_length=400, blank=True)
    advisor = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers appear first.")

    class Meta:
        ordering = ["order", "-end_year"]
        verbose_name_plural = "Education"

    def __str__(self):
        return f"{self.degree}, {self.institution}"


class Experience(models.Model):
    role = models.CharField(max_length=200)
    organization = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    start_year = models.PositiveIntegerField(null=True, blank=True)
    end_year = models.PositiveIntegerField(null=True, blank=True, help_text="Leave empty for current positions.")
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers appear first.")

    class Meta:
        ordering = ["order", "-start_year"]
        verbose_name_plural = "Career"

    def __str__(self):
        return f"{self.role}, {self.organization}"


class Project(models.Model):
    ONGOING = "ongoing"
    COMPLETED = "completed"
    STATUS_CHOICES = [(ONGOING, "Ongoing"), (COMPLETED, "Completed")]

    title = models.CharField(max_length=300)
    slug = models.SlugField(
        max_length=80, unique=True,
        help_text="The project page's web address: /research/<slug>/. Filled in from the title.",
    )
    summary = models.TextField(blank=True, help_text="Short text shown on the Research page card.")
    image = models.ImageField(upload_to="projects/", blank=True)
    role = models.CharField(max_length=200, blank=True, help_text="e.g. Principal Investigator")
    funder = models.CharField(max_length=200, blank=True)
    partners = models.CharField("Partners / collaborators", max_length=500, blank=True)
    start_year = models.PositiveIntegerField(null=True, blank=True)
    end_year = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ONGOING)
    body = models.TextField(
        "Full description", blank=True,
        help_text="Shown on the project's own page. Separate paragraphs with a blank line. "
                  "Formatting: <code>## Heading</code>, <code>- list item</code>, <code>**bold**</code>, "
                  "<code>[link text](https://...)</code>.",
    )
    link = models.URLField(
        "Original source page", max_length=500, blank=True,
        help_text="For your reference only (e.g. the old RWTH page). Not shown on the site.",
    )
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers appear first.")

    class Meta:
        ordering = ["order", "-start_year"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("project", args=[self.slug])

    @property
    def has_page(self):
        """Only projects with something beyond the card get a clickable page."""
        return bool(self.body.strip()) or self.images.exists()


def unique_slug(instance, text, max_length=80):
    from django.utils.text import slugify

    base = slugify(text)[:max_length].rstrip("-") or "project"
    slug, n = base, 2
    qs = type(instance).objects.exclude(pk=instance.pk)
    while qs.filter(slug=slug).exists():
        suffix = f"-{n}"
        slug = base[: max_length - len(suffix)] + suffix
        n += 1
    return slug


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="projects/")
    caption = models.CharField(max_length=500, blank=True)
    credit = models.CharField(max_length=200, blank=True, help_text="e.g. © LIH")
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers appear first.")

    class Meta:
        ordering = ["order", "pk"]
        verbose_name = "Photo"

    def __str__(self):
        return self.caption or self.image.name


class Student(models.Model):
    LEVEL_CHOICES = [("phd", "PhD candidate"), ("msc", "MSc student"), ("postdoc", "Postdoctoral researcher"), ("bsc", "BSc student")]
    CURRENT = "current"
    ALUMNI = "alumni"
    STATUS_CHOICES = [(CURRENT, "Current"), (ALUMNI, "Alumni")]

    name = models.CharField(max_length=200)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="phd")
    topic = models.CharField("Research topic", max_length=400, blank=True)
    start_year = models.PositiveIntegerField(null=True, blank=True)
    end_year = models.PositiveIntegerField(null=True, blank=True)
    photo = models.ImageField(upload_to="students/", blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=CURRENT)
    link = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers appear first.")

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    @property
    def initials(self):
        return "".join(part[0] for part in self.name.split()[:2]).upper()


class Publication(models.Model):
    title = models.CharField(max_length=500)
    authors = models.CharField(max_length=500, blank=True)
    venue = models.CharField(max_length=500, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    citations = models.PositiveIntegerField(default=0)
    url = models.URLField(max_length=500, blank=True)
    scholar_id = models.CharField(max_length=100, blank=True, help_text="Set automatically by the Scholar sync.")

    class Meta:
        ordering = ["-year", "-citations"]

    def __str__(self):
        return self.title
