"""
Django settings for project project.

Generated by 'django-admin startproject' using Django 5.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_URL = "/static/"

# Directory for static files to be collected in production
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Additional static file directories (your Angular build files go here)
STATICFILES_DIRS = [
    os.path.join(
        BASE_DIR, "client/dist/client/browser"
    ),  # Replace with your Angular build folder
]
MEDIA_ROOT = os.path.join(
    BASE_DIR, "media"
)  # Set MEDIA_ROOT to a directory in your project
MEDIA_URL = "/media/"  # Define the media URL

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-$x90a0=p#c)!uvx0i+3!da!@nzv)!4#+f_nme=dm0vq$8u8e62"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "api",
    "corsheaders",
    "rest_framework",
    "djoser",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "project.urls"

CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",  # Or the Angular SSR server if it's different
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "client/dist/client/browser")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "project.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",  # Database name
        "USER": "pmongkho",
        "PASSWORD": "",  # Replace with your actual password
        "HOST": "plan-manager.postgres.database.azure.com",
        "PORT": "5432",
        "OPTIONS": {
            "sslmode": "require",  # This is required for Azure PostgreSQL
            "connect_timeout": 60,  # Set the timeout to 10 seconds
        },
        "CONN_MAX_AGE": 600,  # Keep database connections alive for 10 minutes
    }
}
LOGIN_URL = "/login/"  # URL to redirect unauthenticated users to

# export PGHOST=plan-manager.postgres.database.azure.com
# export PGUSER=pmongkho
# export PGPORT=5432
# export PGDATABASE=postgres
# export PGPASSWORD="{your-password}"

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# settings.py

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",  # Redis server location and database number
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "myapp",  # Optional: Prefix for cache keys to avoid key collisions
    }
}

# Optional: Set a default timeout for cached data (in seconds)
CACHE_TTL = 60 * 15  # 15 minutes
