from pathlib import Path
import os
import dj_database_url
from django.contrib.messages import constants as messages
import environ
import json

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
    "goals",
    # third-party
]

# -------------------------
# Middleware
# -------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
     "evaluation.middleware.OverdueEvaluationLockMiddleware",
     "evaluation.senior_middleware.OverdueManagerEvaluationLockMiddleware",

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
                "goals.utils.permissions.role_context",
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
TIME_ZONE = "America/New_York"  # Change to your local timezone
USE_I18N = True
USE_TZ = True  # Enable timezone support

# -------------------------
# Messages → Tailwind classes
# -------------------------
MESSAGE_TAGS = {
    messages.DEBUG: "bg-gray-200 text-gray-800 border border-gray-400",
    messages.INFO: "bg-blue-100 text-blue-800 border border-blue-400",
    messages.SUCCESS: "bg-green-100 text-green-800 border border-green-400",
    messages.WARNING: "bg-yellow-100 text-yellow-800 border-yellow-400",
    messages.ERROR: "bg-red-100 text-red-800 border-red-400",
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
# Email (Local -> Django Mail Viewer, Production -> Postmark)
# -------------------------
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="support@firehousemovers.com")
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Add a prefix everywhere except production
EMAIL_SUBJECT_PREFIX = f"[{APP_ENV.upper()}] " if APP_ENV != "production" else ""

# Toggle: use Postmark's Sandbox token for staging/local (logs only, no delivery)
USE_POSTMARK_SANDBOX = os.getenv("USE_POSTMARK_SANDBOX", "False") == "True"

# Optional app-side QA whitelist for staging/local
# Example .env: STAGING_ALLOWED_RECIPIENTS='["qa@company.com","dev@company.com"]'
try:
    STAGING_ALLOWED_RECIPIENTS = set(json.loads(os.getenv("STAGING_ALLOWED_RECIPIENTS", "[]")))
except Exception:
    STAGING_ALLOWED_RECIPIENTS = set()

# Resolve Postmark credentials per env
if APP_ENV == "production":
    POSTMARK_TOKEN = os.getenv("POSTMARK_PRODUCTION_SERVER_TOKEN", "")
    POSTMARK_STREAM = os.getenv("POSTMARK_PRODUCTION_MESSAGE_STREAM", "outbound")
else:
    # local and staging both point to staging server (or sandbox)
    if USE_POSTMARK_SANDBOX:
        POSTMARK_TOKEN = "POSTMARK_API_TEST"  # Postmark sandbox -> no delivery, logs visible
    else:
        POSTMARK_TOKEN = os.getenv("POSTMARK_STAGING_SERVER_TOKEN", "")
    POSTMARK_STREAM = os.getenv("POSTMARK_STAGING_MESSAGE_STREAM", "outbound-staging")

ANYMAIL = {
    "POSTMARK_SERVER_TOKEN": POSTMARK_TOKEN,
    "WEBHOOK_SECRET": os.getenv("POSTMARK_WEBHOOK_SECRET", ""),  # if you enable signed webhooks
    "SEND_DEFAULTS": {
        "tags": [f"env:{APP_ENV}"],               # easy filtering in Activity
        "metadata": {"app_env": APP_ENV},
        "track_opens": True,
        "track_clicks": True,
        "esp_extra": {"MessageStream": POSTMARK_STREAM},
    },
}

# -------------------------
# Email configuration (local vs production)
# -------------------------
if DEBUG:
    # Development: Django Mail Viewer for local testing
    INSTALLED_APPS += ["django_mail_viewer"]
    EMAIL_BACKEND = "django_mail_viewer.backends.locmem.EmailBackend"
    DJANGO_MAIL_VIEWER = {
        "OPTIONS": {
            "EMAIL_HOST": "localhost",
            "EMAIL_PORT": 1025,
            "EMAIL_USE_TLS": False,
            "EMAIL_USE_SSL": False,
        }
    }
else:
    # Production: Use Postmark via Anymail
    INSTALLED_APPS += ["anymail"]
    EMAIL_BACKEND = "anymail.backends.postmark.EmailBackend"



# (SMTP fallbacks unused w/ Postmark, harmless to keep)
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")


# -------------------------
# Caching Configuration
# -------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,  # 5 minutes default
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
            'CULL_FREQUENCY': 3,
        }
    },
    'analytics': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'analytics-cache',
        'TIMEOUT': 1800,  # 30 minutes for analytics data
        'OPTIONS': {
            'MAX_ENTRIES': 100,
            'CULL_FREQUENCY': 2,
        }
    }
}

# Cache settings for different environments
if APP_ENV == "production":
    # Use Redis for production (if available)
    CACHES['default'] = {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'TIMEOUT': 300,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
    CACHES['analytics'] = {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/2'),
        'TIMEOUT': 1800,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }

# -------------------------
# Default PK
# -------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
