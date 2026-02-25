from pathlib import Path
from decouple import config
from datetime import timedelta
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# ========================
# SECURITY
# ========================
SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", cast=bool)

ALLOWED_HOSTS = ['*']  # on sécurisera après

# ========================
# APPLICATIONS
# ========================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "corsheaders",

    # Local
    "core",
]

# ========================
# MIDDLEWARE
# ========================
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",

    # ✅ OBLIGATOIRE POUR ADMIN
    "django.contrib.sessions.middleware.SessionMiddleware",

    "django.middleware.common.CommonMiddleware",

    # ✅ OBLIGATOIRE POUR ADMIN
    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ========================
# URLS / WSGI
# ========================
ROOT_URLCONF = "agro_platform.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "agro_platform.wsgi.application"

# ========================
# DATABASE
# ========================
DATABASES = {
    'default': dj_database_url.parse(
        config("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=True
    )
}

# ========================
# AUTH
# ========================
AUTH_USER_MODEL = "core.User"

AUTHENTICATION_BACKENDS = [
    "core.backends.EmailBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# ========================
# REST FRAMEWORK (JWT ONLY)
# ========================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

# ========================
# JWT CONFIG
# ========================
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ========================
# CORS
# ========================
CORS_ALLOW_CREDENTIALS = False  # ❌ PAS DE COOKIES
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]

# ✅ OBLIGATOIRE POUR PUT / POST / PATCH depuis Vue
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
]

# ========================
# I18N
# ========================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ========================
# STATIC
# ========================
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
