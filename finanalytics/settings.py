"""
Django settings for finanalytics project.
"""

from pathlib import Path
import os

# ----------------------------------------------------------
# BASE SETUP
# ----------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-g#%qsqkzt^6)j1ilkabpyht(v+o4o+%k18gv=x%u$@suvn=w-1'

DEBUG = True
ALLOWED_HOSTS = []

# ----------------------------------------------------------
# APPLICATIONS
# ----------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'finanalytics.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'finanalytics.wsgi.application'

# ----------------------------------------------------------
# DATABASE (Django ORM)
# ----------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ----------------------------------------------------------
# CLICKHOUSE CONNECTION (used directly in code)
# ----------------------------------------------------------
CLICKHOUSE = {
    'HOST': os.environ.get('CLICKHOUSE_HOST', 'localhost'),
    'PORT': int(os.environ.get('CLICKHOUSE_PORT', 8123)),
    'USER': os.environ.get('CLICKHOUSE_USER', 'root'),
    'PASSWORD': os.environ.get('CLICKHOUSE_PASSWORD', 'password'),
    'DATABASE': os.environ.get('CLICKHOUSE_DATABASE', 'financial_data'),
}

# ----------------------------------------------------------
# PASSWORD VALIDATION
# ----------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ----------------------------------------------------------
# INTERNATIONALIZATION
# ----------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ----------------------------------------------------------
# STATIC FILES
# ----------------------------------------------------------
STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
