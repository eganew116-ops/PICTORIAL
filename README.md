# Laser Job Logger

Website operasional berbasis Python untuk pencatatan job produksi Laser dan UV.

Stack aktif:

- Django
- PostgreSQL
- Render

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

Deploy production memakai `render.yaml` di root project.

Panduan lengkap ada di `DEPLOY_RENDER_POSTGRES.md`.
