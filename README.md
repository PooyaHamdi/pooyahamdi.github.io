# Dr. Pooya Hamdi: personal website

Django site with four pages (About, Research, Publications, Team). All content is edited in the built-in admin at `/admin`.

## Run locally

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py loaddata content/site.json   # load the site content
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

## Publishing to GitHub Pages

The admin only runs on your computer. The public site is plain HTML, built by a GitHub Action and served on GitHub Pages.

1. Run the site locally and edit content in `/admin`.
2. Every save rewrites `content/site.json`. Uploaded photos and the CV go into `media/`.
3. Commit and push both:

   ```bash
   git add content media
   git commit -m "Update site content"
   git push
   ```

4. The **Build and deploy site** action loads `content/site.json` into a fresh database, runs the tests, renders each page to HTML with `manage.py build_site`, and publishes it.

`db.sqlite3` is not committed, so your admin login never ends up on GitHub. On a new computer, run `loaddata content/site.json` to get the current content.

To preview the static build locally:

```bash
.venv/bin/python manage.py build_site --output _site
python3 -m http.server -d _site 8001
```

### One-time GitHub setup

1. Create the repository on GitHub and push.
2. Under **Settings → Pages**, set **Source** to **GitHub Actions**.
3. To deploy from a branch other than `main`, add that branch under **Settings → Environments → github-pages → Deployment branches**.

The action works out the URL prefix itself. A project page is served at `/<repo>/`. A custom domain or a `<user>.github.io` repository is served at `/`.

Replacing a photo in the admin does not delete the old file from `media/`. Delete unused files by hand before committing if you want to keep the repository small.
