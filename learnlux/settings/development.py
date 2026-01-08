"""
Development Django settings for learnlux project.
"""

from .base import *  # noqa: F401, F403

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-dev-key-not-for-production-use-only"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]


# Database

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}


# Email backend - console for development

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# Static files - simplified for development

STATICFILES_DIRS = [BASE_DIR / "static"]  # noqa: F405
