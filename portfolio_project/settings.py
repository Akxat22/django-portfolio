import os  # <-- ADD THIS IMPORT AT THE TOP
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# --- FIX 1: HIDE YOUR SECRET KEY ---
# Your key is now read from an Environment Variable in Render
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-default-key-for-local-dev')

# --- FIX 2: SET DEBUG TO FALSE ---
# Never run with DEBUG = True in production
DEBUG = False

# --- FIX 3: ADD YOUR RENDER URL ---
ALLOWED_HOSTS = [
    'django-portfolio-g8xj.onrender.com',
    '127.0.0.1', # For local testing
    'localhost',   # For local testing
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',  # <-- ADD THIS
    'django.contrib.staticfiles',
    'portfolio',
    'ckeditor',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # <-- ADD THIS
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # ... rest of your middleware
]

# ... (Keep ROOT_URLCONF, TEMPLATES, WSGI_APPLICATION, MEDIA_URL, MEDIA_ROOT, DATABASES, etc.)

# ...

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# --- FIX 4: ADD STATIC FILE SETTINGS FOR PRODUCTION ---
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'