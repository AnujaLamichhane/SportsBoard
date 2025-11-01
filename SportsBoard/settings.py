# Django settings for SportsBoard project.
from dotenv import load_dotenv
import os
from pathlib import Path


  # <-- this will load all variables from .env

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv()
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'


# ALLOWED_HOSTS is not strictly required when DEBUG is True,
# but keeping it is harmless.
ALLOWED_HOSTS = ['127.0.0.1','localhost']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'matches',
    'homepage',
    # 'accounts',
    'accounts.apps.AccountsConfig',


    'crispy_forms',
    'crispy_bootstrap5',

    # django-allauth apps
    'django.contrib.sites',  # Required by allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',  # For Google
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',  # Allauth middleware
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

SITE_ID = 2 # Required for django.contrib.sites (for allauth)

# --- django-allauth Specific Settings ---
# Authentication backends (unified and correct)
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Required for Django admin
    'allauth.account.auth_backends.AuthenticationBackend',  # For allauth methods (email, social)
]

ACCOUNT_AUTHENTICATION_METHOD = "username_email"  # <--- CHANGED: Allows login with either username or email
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = True  # User must still provide a username
ACCOUNT_EMAIL_VERIFICATION = "mandatory"  # Or "optional" if you don't want to force email verification
LOGIN_REDIRECT_URL = '/'  # Where to go after a successful login
ACCOUNT_LOGOUT_REDIRECT_URL = '/accounts/login/'  # Where to go after logout
LOGIN_URL = '/accounts/login/'  # The URL where allauth's login form is located

# Forms customisation (if you have them; comment out if not using yet)
# ACCOUNT_FORMS = {
#     'login': 'accounts.forms.MyCustomLoginForm',
#     'signup': 'accounts.forms.MyCustomSignupForm',
# }

ROOT_URLCONF = 'SportsBoard.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Add your project-level templates directory if you have one
        'DIRS': [BASE_DIR / 'templates'],  # Example: Project-wide templates folder
        'APP_DIRS': True,  # This tells Django to look for 'templates' in each app
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',  # Good to have for DEBUG=True
                'django.template.context_processors.request',  # Required by allauth
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'SportsBoard.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kathmandu'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'

# Correctly configure STATICFILES_DIRS to find static assets within your apps
STATICFILES_DIRS = [
    BASE_DIR / "static",  # For any project-level static files
    BASE_DIR / "accounts" / "static",  # Explicitly include your accounts app's static files
    # Add other app's static directories if they have them:
    # BASE_DIR / "homepage" / "static",
    # BASE_DIR / "matches" / "static",
]

# STATIC_ROOT is for `collectstatic` in production.
# Ensure it's outside of any app's directory.
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# Email settings for allauth's verification (essential if ACCOUNT_EMAIL_VERIFICATION is 'mandatory')
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # For development: prints emails to console
# For production, you'd use a real email backend like SendGrid, Mailgun, etc.
# EMAIL_HOST = 'smtp.example.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your_email@example.com'
# EMAIL_HOST_PASSWORD = 'your_email_password'
# DEFAULT_FROM_EMAIL = 'webmaster@example.com'
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        # 'APP': {
        #     'client_id': os.getenv('GOOGLE_CLIENT_ID'),
        #     'secret': os.getenv('GOOGLE_SECRET_KEY'),
        #     'key': '',  # Usually empty for Google
        # },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
    }
}
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"
SOCIALACCOUNT_AUTO_SIGNUP = True
ACCOUNT_SIGNUP_REDIRECT_URL = '/your-redirect-url/'
# Skip the intermediate confirmation page
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_ADAPTER = 'accounts.adapters.CustomSocialAccountAdapter'

# Session settings for Remember Me
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_SAVE_EVERY_REQUEST = True