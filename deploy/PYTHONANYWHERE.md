# Deploy to PythonAnywhere

One web app on `https://USERNAME.pythonanywhere.com` serves both the API (`/api/`, `/admin/`)
and the React build (everything else). Telegram gets HTTPS for free and there is no CORS.

## 1. Code

```bash
cd ~
git clone https://github.com/Ziyodullodev/bagzz-backend.git
git clone -b build --single-branch https://github.com/Ziyodullodev/bagzz-frontend.git bagzz-frontend-dist
```

The `build` branch of the frontend repo holds the compiled `dist/` (Vite build with same-origin `/api`).

## 2. Virtualenv (Python 3.12 or newer, Django 6 needs it)

```bash
python3.13 -m venv ~/.virtualenvs/bagzz
~/.virtualenvs/bagzz/bin/pip install -r ~/bagzz-backend/requirements.txt
```

## 3. Environment

```bash
cd ~/bagzz-backend && cp .env.example .env
```

Set at least:

```
DJANGO_SECRET_KEY=<long random string>
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=USERNAME.pythonanywhere.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://USERNAME.pythonanywhere.com
CORS_ALLOWED_ORIGINS=https://USERNAME.pythonanywhere.com
TELEGRAM_BOT_TOKEN=<from @BotFather>
TELEGRAM_DEV_AUTH=false
FRONTEND_DIST=/home/USERNAME/bagzz-frontend-dist
```

## 4. Database and static files

```bash
cd ~/bagzz-backend
~/.virtualenvs/bagzz/bin/python manage.py migrate
~/.virtualenvs/bagzz/bin/python manage.py seed_catalog --if-empty
~/.virtualenvs/bagzz/bin/python manage.py collectstatic --noinput
~/.virtualenvs/bagzz/bin/python manage.py createsuperuser
```

## 5. Web tab

| Setting | Value |
| --- | --- |
| Source code | `/home/USERNAME/bagzz-backend` |
| Working directory | `/home/USERNAME/bagzz-backend` |
| Virtualenv | `/home/USERNAME/.virtualenvs/bagzz` |
| WSGI file | contents of `deploy/pythonanywhere_wsgi.py` |
| Force HTTPS | on |

Static files mappings:

| URL | Directory |
| --- | --- |
| `/static/` | `/home/USERNAME/bagzz-backend/staticfiles` |
| `/media/` | `/home/USERNAME/bagzz-backend/media` |
| `/assets/` | `/home/USERNAME/bagzz-frontend-dist/assets` |

Press **Reload**.

## 6. Telegram

@BotFather → your bot → Bot Settings → Menu Button → `https://USERNAME.pythonanywhere.com/`.

## Updating

```bash
cd ~/bagzz-backend && git pull && ~/.virtualenvs/bagzz/bin/pip install -r requirements.txt \
  && ~/.virtualenvs/bagzz/bin/python manage.py migrate && ~/.virtualenvs/bagzz/bin/python manage.py collectstatic --noinput
cd ~/bagzz-frontend-dist && git pull
```

Then press **Reload** on the Web tab.
