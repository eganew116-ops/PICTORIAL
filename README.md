# PICTORIAL

Website operasional berbasis Python untuk pencatatan job produksi Laser dan UV.

Stack aktif:

- Django
- SQLite
- PythonAnywhere

Kode aplikasi utama ada di `backend_django/`.

## Jalankan Lokal

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r backend_django\requirements.txt
cd backend_django
copy .env.example .env
python manage.py migrate
python manage.py seed_defaults
python manage.py runserver
```

Buka `http://127.0.0.1:8000/`.

## Test

```powershell
cd backend_django
..\.venv\Scripts\python manage.py check
..\.venv\Scripts\python manage.py test
```

## Deploy

Deploy online gratis memakai PythonAnywhere free account dengan database SQLite.

Panduan lengkap ada di `DEPLOY_PYTHONANYWHERE_SQLITE.md`.
