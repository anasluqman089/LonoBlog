# LonoBlog

*Hello eveyrone* This is my personal blog and project page. I made it with a Frutiger Aero look. It is inspired by the 2000s. The blog doesnt need you to log in but not because Im lazy to do it.

## The pages

- `/` is the home page.
- `/blog` is where I post stories.
- `/projects` is where I show my software and electronics projects.
- `/studio` is where I write posts and manage my projects (Only I can acess it).

## Features

I can write posts with Markdown, paste pictures into a post, and preview it
before publishing. People can leave comments and like posts. When I'm signed
in, I can delete comments too.

I can add, edit, and delete projects from the Studio. Each project can have a
description, a list of tools or parts, a link, and a cover image.

## Testing

I first run it using localhost

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python app.py
```

Then I open `http://localhost:8000`.

## Put it on PythonAnywhere

The I put it in PythonAnywhere. I use PythonAnywhere to host the Flask app. I clone the repos using the bash consoles

```sh
git clone https://github.com/anasluqman089/LonoBlog.git
cd LonoBlog
mkvirtualenv --python=/usr/bin/python3.13 lonoblog-venv
pip install -r requirements.txt
```

Then I create a web app from the Web tab using Manual configuration
and the same Python version (Python 3.13). I set the virtualenv to
`/home/Lonos67/.virtualenvs/lonoblog-venv` and edit the WSGI file to load
my app:

```python
import os
import sys

path = "/home/Lonos67/LonoBlog"
if path not in sys.path:
    sys.path.insert(0, path)

os.environ["Hash"] = "....."
os.environ["Secret"] = "...."
os.environ["Session cookie secret"] = "true"

from app import app as application
```

the secret password hash was created in the bash consoles using the command:

```sh
python -c 'from getpass import getpass; from werkzeug.security import generate_password_hash; print(generate_password_hash(getpass("Studio password: ")))'
```

