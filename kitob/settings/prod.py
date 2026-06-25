from .base import *

# Replace 'yourusername' with your actual PythonAnywhere username
ALLOWED_HOSTS = [
    'yourusername.pythonanywhere.com',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/home/yourusername/pdefai-backend/db.sqlite3',
    }
}

CORS_ALLOWED_ORIGINS = [
    'https://yourusername.pythonanywhere.com',
]

STATIC_URL = '/static/'
STATIC_ROOT = '/home/yourusername/pdefai-backend/staticfiles/'
