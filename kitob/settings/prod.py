from .base import *

ALLOWED_HOSTS = [
    'dovudbekmm.pythonanywhere.com',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/home/dovudbekmm/pdefai-backend/db.sqlite3',
    }
}

CORS_ALLOWED_ORIGINS = [
    'https://dovudbekmm.pythonanywhere.com',
    'https://muslihun.vercel.app',
]

STATIC_URL = '/static/'
STATIC_ROOT = '/home/dovudbekmm/pdefai-backend/staticfiles/'
