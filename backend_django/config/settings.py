import os
from pathlib import Path
from urllib.parse import urlparse

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-key-change-me")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost,testserver").split(",")
    if host.strip()
]

pythonanywhere_domain = os.getenv("PYTHONANYWHERE_DOMAIN", "").strip()
if pythonanywhere_domain and pythonanywhere_domain not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(pythonanywhere_domain)

app_base_url = os.getenv("APP_BASE_URL", "").strip()
if app_base_url:
    parsed_app_url = urlparse(app_base_url)
    if parsed_app_url.hostname and parsed_app_url.hostname not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(parsed_app_url.hostname)

csrf_trusted_origins = [
    origin.strip()
    for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")
    if origin.strip()
]
if pythonanywhere_domain:
    pythonanywhere_url = f"https://{pythonanywhere_domain}"
    if pythonanywhere_url not in csrf_trusted_origins:
        csrf_trusted_origins.append(pythonanywhere_url)
if app_base_url and app_base_url not in csrf_trusted_origins:
    csrf_trusted_origins.append(app_base_url)
CSRF_TRUSTED_ORIGINS = csrf_trusted_origins

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "operations",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

database_url = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
DATABASES = {
    "default": dj_database_url.parse(
        database_url,
        conn_max_age=600,
        ssl_require=database_url.startswith("postgres"),
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "id"
TIME_ZONE = "Asia/Jakarta"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
