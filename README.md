# Dr. Pooya Hamdi: personal website

Django site with four pages (About, Research, Publications, Team). All content is edited in the built-in admin at `/admin`.

## Run locally

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_site          # starting content (once)
.venv/bin/python manage.py createsuperuser    # your admin login
.venv/bin/python manage.py runserver
```

Open http://127.0.0.1:8000. The editor is at http://127.0.0.1:8000/admin.

## Editing content (admin)

| Admin section | What it controls |
|---|---|
| Profile | Name, title, bio, photo, and the Google Scholar / LinkedIn / email / CV links |
| Education | The education ladder on the About page. Lower `order` numbers appear first. |
| Projects | Research page cards, grouped as Ongoing or Completed |
| Students | Team page: current students get cards, alumni get a list |
| Publications | Publications page. Tick **featured** to list a paper under "Selected publications". |
| Citation statistics | The numbers and chart on the About page, plus a **Refresh citations from Google Scholar** button |

Entries containing `TODO` are placeholders to replace.

## Citations from Google Scholar

```bash
.venv/bin/python manage.py update_scholar
```

This reads the public Scholar profile and updates the citation numbers, the per-year chart, and each paper's citation count. New papers are added automatically. Your manual edits (such as `featured`) are kept.

Scholar has no official API and sometimes refuses automated requests. When that happens, the command reports an error and the existing numbers stay as they are. You can always type the numbers in by hand under **Citation statistics**. To run it automatically, schedule the command weekly on the host.

## Deploying

Set these environment variables:

- `DJANGO_DEBUG=0`
- `DJANGO_SECRET_KEY=<random>`
- `DJANGO_ALLOWED_HOSTS=yourdomain.com`
- `DJANGO_CSRF_TRUSTED_ORIGINS=https://yourdomain.com`

Then run `collectstatic` and serve the site with `gunicorn config.wsgi`.

The host must also serve uploaded photos and the CV from `media/`. For example, use a static-files mapping on PythonAnywhere or a persistent disk on Render.
