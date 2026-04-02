# Django + SQLite + PythonAnywhere

## Stack Final

Website operasional ini sekarang memakai:

- Django sebagai aplikasi web
- SQLite sebagai database
- PythonAnywhere sebagai hosting online

Target ini dipilih karena gratis dan tidak perlu setup PostgreSQL terpisah untuk tahap awal.

## Sebelum Upload

Pastikan project sudah ada di GitHub.

Repo aktif berisi:

- `backend_django/`
- `README.md`
- `DEPLOY_PYTHONANYWHERE_SQLITE.md`

## Buat Akun PythonAnywhere

1. Daftar akun di `https://www.pythonanywhere.com/`
2. Login ke dashboard PythonAnywhere

## Buat Web App Django

1. Buka tab `Web`
2. Klik `Add a new web app`
3. Pilih domain gratis `yourusername.pythonanywhere.com`
4. Pilih `Manual configuration`
5. Pilih Python `3.11`

## Clone Project Dari GitHub

Buka `Bash console`, lalu jalankan:

```bash
git clone https://github.com/eganew116-ops/PICTORIAL.git
cd PICTORIAL
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r backend_django/requirements.txt
```

## Siapkan Environment

Masuk ke folder aplikasi:

```bash
cd ~/PICTORIAL/backend_django
cp .env.example .env
```

Edit `.env` lalu sesuaikan minimal nilai ini:

```env
SECRET_KEY=ganti-dengan-secret-yang-aman
DEBUG=false
ALLOWED_HOSTS=yourusername.pythonanywhere.com
CSRF_TRUSTED_ORIGINS=https://yourusername.pythonanywhere.com
PYTHONANYWHERE_DOMAIN=yourusername.pythonanywhere.com
APP_BASE_URL=https://yourusername.pythonanywhere.com
DATABASE_URL=sqlite:///db.sqlite3
DJANGO_SUPERUSER_USERNAME=operator
DJANGO_SUPERUSER_EMAIL=operator@example.com
DJANGO_SUPERUSER_PASSWORD=ganti-password-login
```

## Jalankan Setup Django

Masih di folder `backend_django`, jalankan:

```bash
source ~/PICTORIAL/.venv/bin/activate
python manage.py migrate
python manage.py seed_defaults
python manage.py collectstatic --noinput
```

## Set Virtualenv Di PythonAnywhere

Di tab `Web`, isi:

- `Source code`: `/home/yourusername/PICTORIAL/backend_django`
- `Working directory`: `/home/yourusername/PICTORIAL/backend_django`
- `Virtualenv`: `/home/yourusername/PICTORIAL/.venv`

## Isi File WSGI PythonAnywhere

Di tab `Web`, buka file WSGI lalu ganti isinya menjadi:

```python
import os
import sys

path = "/home/yourusername/PICTORIAL/backend_django"
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
```

## Static Files

Di tab `Web`, tambahkan static mapping:

- URL: `/static/`
- Directory: `/home/yourusername/PICTORIAL/backend_django/staticfiles`

## Reload Website

Klik `Reload` di tab `Web`.

Lalu buka:

- `https://yourusername.pythonanywhere.com/login/`

Login dengan:

- username: `operator`
- password: nilai `DJANGO_SUPERUSER_PASSWORD`

## Catatan Penting

- SQLite di PythonAnywhere akan tersimpan online di akun/server PythonAnywhere, bukan di komputer lokal kamu.
- Free account PythonAnywhere cocok untuk tahap awal dan demo.
- Kalau nanti traffic dan kebutuhan data membesar, baru pindah ke PostgreSQL dan hosting yang lebih kuat.
