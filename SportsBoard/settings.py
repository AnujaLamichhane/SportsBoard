from dotenv import load_dotenv
import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()

# ─────────────────────────────────────────
# CORE SETTINGS
# ─────────────────────────────────────────

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-key-for-dev-only')

DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,sportsboard.onrender.com').split(',')

# This looks for the environment variable, but provides defaults if not found
csrf_default = 'https://sportsboard.onrender.com,http://localhost,http://127.0.0.1'
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', csrf_default).split(',')

# CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', 'http://localhost').split(',')

# ─────────────────────────────────────────
# INSTALLED APPS
# ─────────────────────────────────────────

INSTALLED_APPS = [

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary_storage',
    'cloudinary',
    'admin_panel',
    'homepage',
    'organizer',
    'payments',
    'accounts.apps.AccountsConfig',

    'crispy_forms',
    'crispy_bootstrap5',
    'news',

    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',




]

# ─────────────────────────────────────────
# MIDDLEWARE
# ─────────────────────────────────────────

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',   # Must be second, right after SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'SportsBoard.urls'

# ─────────────────────────────────────────
# TEMPLATES
# ─────────────────────────────────────────

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'homepage.context_processors.sports_menu',
            ],
        },
    },
]

WSGI_APPLICATION = 'SportsBoard.wsgi.application'

# ─────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────

# In production (Render), DATABASE_URL env var is set automatically.
# Locally, it falls back to SQLite.
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=0,
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ─────────────────────────────────────────
# PASSWORD VALIDATION
# ─────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─────────────────────────────────────────
# INTERNATIONALIZATION
# ─────────────────────────────────────────

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kathmandu'
USE_I18N = True
USE_TZ = True

# ─────────────────────────────────────────
# STATIC & MEDIA FILES
# ─────────────────────────────────────────

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Only include dirs that actually exist to avoid collectstatic crashes
_static_dirs = [
    BASE_DIR / 'static',
    BASE_DIR / 'accounts' / 'static',
    BASE_DIR / 'organizer' / 'static',
    BASE_DIR / 'admin_panel' / 'static',
    BASE_DIR / 'news' / 'static',
]
STATICFILES_DIRS = [d for d in _static_dirs if d.exists()]

# Whitenoise compression for production
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



# ─────────────────────────────────────────
# CRISPY FORMS
# ─────────────────────────────────────────

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# ─────────────────────────────────────────
# EMAIL
# ─────────────────────────────────────────

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASS')
DEFAULT_FROM_EMAIL = f"SportsBoard <{os.getenv('EMAIL_USER')}>"

# ─────────────────────────────────────────
# DJANGO ALLAUTH
# ─────────────────────────────────────────

# SITE_ID must match the domain entry in django_site table.
# Set to 1 for fresh deployments (default site created by migrations).
# If your production site breaks on login, run:
#   python manage.py shell
#   from django.contrib.sites.models import Site
#   Site.objects.update_or_create(id=1, defaults={'domain': 'your-app.onrender.com', 'name': 'SportsBoard'})
SITE_ID = int(os.getenv('SITE_ID', '1'))

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ACCOUNT_LOGIN_METHODS = {'username', 'email'}
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_LOGOUT_REDIRECT_URL = '/accounts/login/'
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = 'accounts:dashboard_redirect'
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '/accounts/login/'
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = '/'

# Use https in production, http locally
ACCOUNT_DEFAULT_HTTP_PROTOCOL = os.getenv('ACCOUNT_HTTP_PROTOCOL', 'http')

ACCOUNT_ADAPTER = 'accounts.adapters.CustomAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'accounts.adapters.CustomSocialAccountAdapter'
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_SIGNUP_REDIRECT_URL = '/accounts/login/?verify_email=true'
SOCIALACCOUNT_STORE_TOKENS = True
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {
            'access_type': 'online',
            'prompt': 'select_account',
        },
    }
}

# ─────────────────────────────────────────
# PAYMENTS
# ─────────────────────────────────────────

KHALTI_SECRET_KEY = os.getenv('KHALTI_SECRET_KEY')

# ─────────────────────────────────────────
# SESSION
# ─────────────────────────────────────────

SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True


import mimetypes
mimetypes.add_type("text/css", ".css", True)
mimetypes.add_type("application/javascript", ".js", True)
mimetypes.add_type("video/mp4", ".mp4", True)

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET')
}
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'



# 4. Fix Email Backend Logic
if not DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    # Force HTTPS for email links on Render
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http'

X_FRAME_OPTIONS = 'ALLOWALL'