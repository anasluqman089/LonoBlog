# LonoBlog

Anas's personal blog and writing studio, backed by Flask and SQLite. The home
page introduces the site; the studio creates, edits, and stores stories in
`blog.sqlite3` on the server.

The site uses a Frutiger Aero-inspired sky-and-hills wallpaper with cool blue
glass surfaces, soft highlights, and rounded controls.

The writing studio and story API are protected by a password. The password is
stored as a salted hash in the ignored local `.env` file.

## Run locally

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python app.py
```

Open `http://localhost:8000` for the LonoBlog home page, `/blog` for published
stories, `/projects` for the public portfolio, or `/studio` to write and manage
projects. The Projects tab in the protected studio lets you add, edit, and
delete software, electronics, and other projects, including descriptions,
technologies/components, links, and optional cover images.

Blog posts support GitHub-style Markdown: headings, emphasis, lists, task lists,
tables, quotes, links, images, and fenced code blocks. Paste a copied image into
the story editor to upload it and insert its Markdown image link. Raw HTML is
displayed as text. The studio provides Markdown formatting controls, an emoji
bar, and a live preview; comments also have an emoji bar. Posts show estimated
reading times, have copyable direct links, per-browser likes, and comments.
Comments require a name and are limited to 1,000 characters, with a 30-second
pause between comments from the same browser. The blog page has 20 scattered
hand-drawn doodles and a softer, rounded layout. The password entry is
available in the home page footer. `.env` contains the local password hash; it
is excluded from Git. To set a different password, generate a salted hash
with `.venv/bin/python -c 'from getpass import getpass; from werkzeug.security import generate_password_hash; print(generate_password_hash(getpass("New studio password: ")))'`
and set it as `BLOG_PASSWORD_HASH` in `.env`. Use a strong password before
exposing the app beyond your private development environment.

## API

- `GET /api/stories` lists all stories; `?status=draft` or `?status=published`
	filters the list.
- `GET /api/public/stories` lists published stories for the public blog page.
- `GET /api/public/projects` lists projects for the public portfolio page.
- `POST /api/public/stories/<id>/like` toggles the current browser's like.
- `GET /api/public/stories/<id>/comments` lists comments on a published story.
- `POST /api/public/stories/<id>/comments` adds a comment to a published story.
- `DELETE /api/comments/<comment-id>` deletes a comment (studio access required).
- `POST /api/stories` creates a draft or published story.
- `PUT /api/stories/<id>` updates a story.
- `DELETE /api/stories/<id>` deletes a story.
- `GET`, `POST /api/projects` list and create projects (studio access required).
- `PUT`, `DELETE /api/projects/<id>` update and delete projects (studio access required).