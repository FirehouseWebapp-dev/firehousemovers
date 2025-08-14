from pathlib import Path
import os
import dj_database_url
from django.contrib.messages import constants as messages
import environ

env = environ.Env()

# -------------------------
# Paths / env
# -------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(env_file=str(BASE_DIR / ".env"))

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-sx_hvwar&4xvjixh@pr+2&m_#$wa*gkjetdou_hb-#1@!gi2al",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "False") == "True"
APP_ENV = os.getenv("APP_ENV", "local").lower()  # local | staging | production

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "fire-house-movers-7f0b30006c85.herokuapp.com",
]

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# -------------------------
# Static / media
# -------------------------
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static/"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# -------------------------
# Core installed apps
# -------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # project apps
    "inventory_app",
    "authentication",
    "vehicle",
    "station",
    "gift",
    "inspection",
    "packaging_supplies",
    "marketing",
    "widget_tweaks",
    "evaluation",
    # third‑party
    "anymail",  # keep defined here; we’ll switch backend per env below
]

# -------------------------
# Middleware
# -------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "evaluation.middleware.EvaluationLockMiddleware",
]

# -------------------------
# Templates
# -------------------------
ROOT_URLCONF = "firehousemovers.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "inventory_app.context_processors.low_stock_processor",
            ],
        },
    },
]

WSGI_APPLICATION = "firehousemovers.wsgi.application"

# -------------------------
# Database
# -------------------------
if "DATABASE_URL" in os.environ:
    DATABASES = {"default": dj_database_url.config(conn_max_age=600, ssl_require=True)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": os.getenv("POSTGRES_DB", "fire_house_db"),
            "USER": os.getenv("POSTGRES_USER", "postgres"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", "postgres"),
            "HOST": os.getenv("POSTGRES_HOST", "localhost"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
        }
    }

# -------------------------
# Auth / redirects
# -------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_REDIRECT_URL = "/profile/"
LOGOUT_REDIRECT_URL = "/"
LOGIN_URL = "authentication:login"
LOGOUT_URL = "authentication:logout"

# -------------------------
# i18n / tz
# -------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = False

# -------------------------
# Messages → Tailwind classes
# -------------------------
MESSAGE_TAGS = {
    messages.DEBUG: "bg-gray-200 text-gray-800 border border-gray-400",
    messages.INFO: "bg-blue-100 text-blue-800 border border-blue-400",
    messages.SUCCESS: "bg-green-100 text-green-800 border border-green-400",
    messages.WARNING: "bg-yellow-100 text-yellow-800 border border-yellow-400",
    messages.ERROR: "bg-red-100 text-red-800 border border-red-400",
}

# -------------------------
# File storage (local vs cloud)
# -------------------------
if DEBUG:
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")
else:
    INSTALLED_APPS += ["cloudinary", "cloudinary_storage"]
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
    CLOUDINARY_STORAGE = {
        "CLOUD_NAME": os.environ.get("CLOUDINARY_CLOUD_NAME"),
        "API_KEY": os.environ.get("CLOUDINARY_API_KEY"),
        "API_SECRET": os.environ.get("CLOUDINARY_API_SECRET"),
        "SECURE": True,
    }

# -------------------------
# Email (Postmark in prod; viewer in local/staging)
# -------------------------
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="aqsakhalidrandom@gmail.com")
SERVER_EMAIL = DEFAULT_FROM_EMAIL

if APP_ENV in ("local", "staging"):
    # Show all emails at /mail/
    EMAIL_BACKEND = 'django_mail_viewer.backends.locmem.EmailBackend'
    INSTALLED_APPS += ["django_mail_viewer"]
    EMAIL_SUBJECT_PREFIX = f"[{APP_ENV.upper()}] "
else:
    # Production → Postmark via Anymail
    EMAIL_BACKEND = "anymail.backends.postmark.EmailBackend"
    ANYMAIL = {
        "POSTMARK_SERVER_TOKEN": os.getenv("POSTMARK_SERVER_TOKEN"),
        "POSTMARK_MESSAGE_STREAM": os.getenv("POSTMARK_MESSAGE_STREAM", "outbound"),
    }
    EMAIL_SUBJECT_PREFIX = ""

# helpful if you ever fall back to SMTP (unused with Postmark backend)
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")

# -------------------------
# Default PK
# -------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
