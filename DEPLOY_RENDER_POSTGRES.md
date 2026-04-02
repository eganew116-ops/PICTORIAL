# Django + PostgreSQL + Render

## Struktur Baru

Website operasional sekarang ada di folder `backend_django/`.

Stack final:

- Django server-rendered website
- PostgreSQL di Render
- Deploy website di Render Web Service

## Local Setup

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

Login default akan dibuat dari env:

- username: `operator`
- email: `operator@example.com`
- password: isi `DJANGO_SUPERUSER_PASSWORD`

## Fitur yang Sudah Disiapkan

- login/logout
- dashboard ringkasan Laser dan UV
- CRUD job Laser
- CRUD job UV
- CRUD pricing rules
- admin Django
- health check `/up/`

## Deploy ke Render

Repo ini sudah punya `render.yaml`.

Yang dibuat:

- 1 Render Postgres database
- 1 Render Python web service untuk Django

## Perlu Login Ke Mana?

Ya, untuk deploy kamu tetap perlu login ke beberapa layanan ini:

- `Render`: ya, wajib. Database PostgreSQL dan website Django akan dibuat di akun Render kamu.
- `GitHub` atau `GitLab`: biasanya ya, karena Render perlu mengambil source code dari repository.
- `Website PostgreSQL` terpisah: tidak perlu. Kalau pakai Render Postgres, tidak ada website PostgreSQL lain yang harus kamu login.
- `Website aplikasi Django`: ya, nanti setelah deploy kamu login sebagai user aplikasi, misalnya `operator`.

Jadi secara praktik, kamu tidak perlu cari atau login ke "website PostgreSQL". Yang kamu butuhkan hanya akun Render, repo code, dan akun login aplikasi Django.

Env penting yang harus kamu isi di Render:

- `SECRET_KEY`
- `DJANGO_SUPERUSER_PASSWORD`

Render akan jalan dengan:

- `buildCommand`: install dependency + collectstatic
- `preDeployCommand`: migrate + seed user default
- `startCommand`: `gunicorn config.wsgi:application --log-file -`

## Langkah Deploy Sampai Live

1. Push project ini ke GitHub atau GitLab.
2. Login ke Render.
3. Pilih `New +` lalu buat service dari `Blueprint`.
4. Hubungkan repo yang berisi project ini.
5. Pastikan Render membaca file `render.yaml` di root project.
6. Isi env rahasia:
   - `SECRET_KEY`
   - `DJANGO_SUPERUSER_PASSWORD`
7. Jalankan deploy.
8. Tunggu sampai web service dan database selesai dibuat.
9. Buka URL website dari Render.
10. Login ke website dengan:
   - username: `operator`
   - password: nilai `DJANGO_SUPERUSER_PASSWORD`
11. Setelah masuk, buat pricing rule Laser dan UV sebelum mulai input data produksi.

## Kalau Mau Cek PostgreSQL

Kamu tidak wajib login ke tool database apa pun untuk sekadar deploy website.

Kalau nanti ingin inspeksi database, opsinya:

- buka dashboard database di Render
- copy connection string PostgreSQL
- connect lewat tool seperti DBeaver, TablePlus, atau `psql`

Tapi ini opsional, bukan langkah wajib untuk publish website.

## Catatan

- Repo ini sekarang sudah dibersihkan ke jalur aktif `backend_django/`.
- Jalur Flutter, Laravel, XAMPP, dan file deploy lama sudah tidak dipakai lagi.
