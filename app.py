import os
import secrets
import sqlite3
import time
import uuid
from datetime import datetime, timedelta, timezone
from functools import wraps
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, g, jsonify, redirect, request, send_from_directory, session, url_for
from werkzeug.security import check_password_hash


ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")
VALID_CATEGORIES = {"Personal", "Ideas", "Work", "Notes"}
VALID_STATUSES = {"draft", "published"}


def require_authorized_user(api=False):
    def decorate(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if session.get("writer_access") is True:
                return view(*args, **kwargs)
            session.clear()
            if api:
                return jsonify(error="Enter the studio password to continue."), 401
            return redirect(url_for("home", sign_in="required"))

        return wrapped

    return decorate


def create_app(database_path=None):
    app = Flask(__name__)
    app.config.update(
        DATABASE=str(database_path or os.environ.get("BLOG_DATABASE", ROOT / "blog.sqlite3")),
        SECRET_KEY=os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32),
        BLOG_PASSWORD_HASH=os.environ.get("BLOG_PASSWORD_HASH"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true",
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
    )
    login_attempts = {}

    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(app.config["DATABASE"]) as database:
        database.execute(
            """
            CREATE TABLE IF NOT EXISTS stories (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                excerpt TEXT NOT NULL DEFAULT '',
                body TEXT NOT NULL DEFAULT '',
                category TEXT NOT NULL,
                status TEXT NOT NULL CHECK (status IN ('draft', 'published')),
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        database.execute(
            """
            CREATE TABLE IF NOT EXISTS story_likes (
                story_id TEXT NOT NULL,
                voter_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY (story_id, voter_id)
            )
            """
        )
        database.execute(
            """
            CREATE TABLE IF NOT EXISTS story_comments (
                id TEXT PRIMARY KEY,
                story_id TEXT NOT NULL,
                voter_id TEXT NOT NULL,
                name TEXT NOT NULL,
                body TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

    def get_database():
        if "database" not in g:
            g.database = sqlite3.connect(app.config["DATABASE"])
            g.database.row_factory = sqlite3.Row
        return g.database

    @app.teardown_appcontext
    def close_database(_error=None):
        database = g.pop("database", None)
        if database is not None:
            database.close()

    def story_json(row):
        return {
            "id": row["id"],
            "title": row["title"],
            "excerpt": row["excerpt"],
            "body": row["body"],
            "category": row["category"],
            "status": row["status"],
            "createdAt": row["created_at"],
            "updatedAt": row["updated_at"],
        }

    def public_story_exists(database, story_id):
        return database.execute(
            "SELECT 1 FROM stories WHERE id = ? AND status = 'published'",
            (story_id,),
        ).fetchone() is not None

    def public_voter_id():
        voter_id = session.get("public_voter_id")
        if not voter_id:
            voter_id = secrets.token_urlsafe(24)
            session["public_voter_id"] = voter_id
        return voter_id

    def parse_story_payload():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return None, "Request body must be a JSON object."

        title = payload.get("title", "")
        excerpt = payload.get("excerpt", "")
        body = payload.get("body", "")
        category = payload.get("category", "Personal")
        status = payload.get("status", "draft")
        if not all(isinstance(value, str) for value in (title, excerpt, body, category, status)):
            return None, "Story fields must be text."

        title = title.strip()
        excerpt = excerpt.strip()
        body = body.strip()
        if not title:
            return None, "A story title is required."
        if len(title) > 120 or len(excerpt) > 240 or len(body) > 1_000_000:
            return None, "Story content exceeds the allowed length."
        if category not in VALID_CATEGORIES:
            return None, "Choose a valid story category."
        if status not in VALID_STATUSES:
            return None, "Choose draft or published status."
        if status == "published" and not body:
            return None, "A published story must include body text."

        return {
            "title": title,
            "excerpt": excerpt,
            "body": body,
            "category": category,
            "status": status,
        }, None

    @app.get("/")
    def home():
        return send_from_directory(ROOT, "home.html")

    @app.get("/blog")
    def blog():
        return send_from_directory(ROOT, "blog.html")

    @app.get("/markdown.js")
    def markdown_script():
        return send_from_directory(ROOT, "markdown.js", mimetype="text/javascript")

    @app.get("/api/public/stories")
    def public_stories():
        database = get_database()
        voter_id = public_voter_id()
        rows = database.execute(
            """
            SELECT stories.*,
                (SELECT COUNT(*) FROM story_likes WHERE story_id = stories.id) AS likes_count,
                (SELECT COUNT(*) FROM story_comments WHERE story_id = stories.id) AS comments_count,
                EXISTS(
                    SELECT 1 FROM story_likes
                    WHERE story_id = stories.id AND voter_id = ?
                ) AS liked
            FROM stories
            WHERE status = 'published'
            ORDER BY updated_at DESC
            """,
            (voter_id,),
        ).fetchall()
        public_stories = []
        for row in rows:
            story = story_json(row)
            story.update(
                likesCount=row["likes_count"],
                commentsCount=row["comments_count"],
                liked=bool(row["liked"]),
            )
            public_stories.append(story)
        return jsonify(public_stories)

    @app.post("/api/public/stories/<story_id>/like")
    def toggle_public_story_like(story_id):
        database = get_database()
        if not public_story_exists(database, story_id):
            return jsonify(error="Published story not found."), 404

        voter_id = public_voter_id()
        liked = database.execute(
            "SELECT 1 FROM story_likes WHERE story_id = ? AND voter_id = ?",
            (story_id, voter_id),
        ).fetchone() is not None
        if liked:
            database.execute(
                "DELETE FROM story_likes WHERE story_id = ? AND voter_id = ?",
                (story_id, voter_id),
            )
        else:
            database.execute(
                "INSERT INTO story_likes (story_id, voter_id, created_at) VALUES (?, ?, ?)",
                (story_id, voter_id, datetime.now(timezone.utc).isoformat(timespec="seconds")),
            )
        database.commit()
        likes_count = database.execute(
            "SELECT COUNT(*) FROM story_likes WHERE story_id = ?",
            (story_id,),
        ).fetchone()[0]
        return jsonify(liked=not liked, likesCount=likes_count)

    @app.get("/api/public/stories/<story_id>/comments")
    def public_story_comments(story_id):
        database = get_database()
        if not public_story_exists(database, story_id):
            return jsonify(error="Published story not found."), 404

        rows = database.execute(
            """
            SELECT id, name, body, created_at FROM story_comments
            WHERE story_id = ? ORDER BY created_at ASC
            """,
            (story_id,),
        ).fetchall()
        return jsonify([
            {
                "id": row["id"],
                "name": row["name"],
                "body": row["body"],
                "createdAt": row["created_at"],
            }
            for row in rows
        ])

    @app.post("/api/public/stories/<story_id>/comments")
    def add_public_story_comment(story_id):
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(error="Comment must be a JSON object."), 400
        name = payload.get("name")
        body = payload.get("body")
        if not isinstance(name, str) or not isinstance(body, str):
            return jsonify(error="Enter your name and comment."), 400
        name = name.strip()
        body = body.strip()
        if not name or not body:
            return jsonify(error="Enter your name and comment."), 400
        if len(name) > 60 or len(body) > 1000:
            return jsonify(error="Name must be 60 characters or fewer and comments 1,000 characters or fewer."), 400

        database = get_database()
        if not public_story_exists(database, story_id):
            return jsonify(error="Published story not found."), 404

        voter_id = public_voter_id()
        previous = database.execute(
            """
            SELECT created_at FROM story_comments
            WHERE voter_id = ? ORDER BY created_at DESC LIMIT 1
            """,
            (voter_id,),
        ).fetchone()
        now = datetime.now(timezone.utc)
        if previous and now - datetime.fromisoformat(previous["created_at"]) < timedelta(seconds=30):
            return jsonify(error="Please wait 30 seconds before posting another comment."), 429

        comment = {
            "id": uuid.uuid4().hex,
            "name": name,
            "body": body,
            "createdAt": now.isoformat(timespec="seconds"),
        }
        database.execute(
            """
            INSERT INTO story_comments (id, story_id, voter_id, name, body, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (comment["id"], story_id, voter_id, name, body, comment["createdAt"]),
        )
        database.commit()
        return jsonify(comment), 201

    @app.get("/api/session")
    def session_status():
        authenticated = session.get("writer_access") is True
        if not authenticated:
            session.clear()
        return jsonify(
            authenticated=authenticated,
            passwordConfigured=bool(app.config["BLOG_PASSWORD_HASH"]),
        )

    @app.post("/api/login")
    def password_login():
        password_hash = app.config["BLOG_PASSWORD_HASH"]
        if not password_hash:
            return jsonify(error="The studio password has not been configured."), 503
        payload = request.get_json(silent=True)
        password = payload.get("password") if isinstance(payload, dict) else None
        if not isinstance(password, str):
            return jsonify(error="Enter the studio password."), 400

        client_ip = request.remote_addr or "unknown"
        now = time.monotonic()
        attempts, locked_until = login_attempts.get(client_ip, (0, 0))
        if locked_until > now:
            return jsonify(error="Too many attempts. Please try again in five minutes."), 429
        if not check_password_hash(password_hash, password):
            attempts += 1
            login_attempts[client_ip] = (0, now + 300) if attempts >= 5 else (attempts, 0)
            return jsonify(error="That password did not match."), 401

        login_attempts.pop(client_ip, None)
        session.clear()
        session.permanent = True
        session["writer_access"] = True
        return jsonify(authenticated=True)

    @app.get("/login")
    def login():
        return redirect(url_for("home", sign_in="required"))

    @app.post("/logout")
    def logout():
        session.clear()
        return redirect(url_for("home"))

    @app.get("/studio")
    @require_authorized_user()
    def studio():
        return send_from_directory(ROOT, "index.html")

    @app.get("/api/stories")
    @require_authorized_user(api=True)
    def list_stories():
        status = request.args.get("status")
        if status and status not in VALID_STATUSES:
            return jsonify(error="Choose draft or published status."), 400

        database = get_database()
        if status:
            rows = database.execute(
                "SELECT * FROM stories WHERE status = ? ORDER BY updated_at DESC",
                (status,),
            ).fetchall()
        else:
            rows = database.execute(
                "SELECT * FROM stories ORDER BY updated_at DESC"
            ).fetchall()
        return jsonify([story_json(row) for row in rows])

    @app.post("/api/stories")
    @require_authorized_user(api=True)
    def create_story():
        story, error = parse_story_payload()
        if error:
            return jsonify(error=error), 400

        story_id = uuid.uuid4().hex
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        database = get_database()
        database.execute(
            """
            INSERT INTO stories (id, title, excerpt, body, category, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                story_id,
                story["title"],
                story["excerpt"],
                story["body"],
                story["category"],
                story["status"],
                now,
                now,
            ),
        )
        database.commit()
        row = database.execute("SELECT * FROM stories WHERE id = ?", (story_id,)).fetchone()
        return jsonify(story_json(row)), 201

    @app.put("/api/stories/<story_id>")
    @require_authorized_user(api=True)
    def update_story(story_id):
        story, error = parse_story_payload()
        if error:
            return jsonify(error=error), 400

        database = get_database()
        existing = database.execute(
            "SELECT created_at FROM stories WHERE id = ?", (story_id,)
        ).fetchone()
        if existing is None:
            return jsonify(error="Story not found."), 404

        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        database.execute(
            """
            UPDATE stories
            SET title = ?, excerpt = ?, body = ?, category = ?, status = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                story["title"],
                story["excerpt"],
                story["body"],
                story["category"],
                story["status"],
                now,
                story_id,
            ),
        )
        database.commit()
        row = database.execute("SELECT * FROM stories WHERE id = ?", (story_id,)).fetchone()
        return jsonify(story_json(row))

    @app.delete("/api/stories/<story_id>")
    @require_authorized_user(api=True)
    def delete_story(story_id):
        database = get_database()
        cursor = database.execute("DELETE FROM stories WHERE id = ?", (story_id,))
        database.commit()
        if cursor.rowcount == 0:
            return jsonify(error="Story not found."), 404
        return "", 204

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)