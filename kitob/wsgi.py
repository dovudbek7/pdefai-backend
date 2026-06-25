import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kitob.settings.dev')

application = get_wsgi_application()

# ─── PythonAnywhere WSGI fayl (/var/www/yourusername_pythonanywhere_com_wsgi.py) ───
#
# import os, sys
# path = '/home/yourusername/pdefai-backend'
# if path not in sys.path:
#     sys.path.insert(0, path)
# os.environ['DJANGO_SETTINGS_MODULE'] = 'kitob.settings.prod'
# from django.core.wsgi import get_wsgi_application
# application = get_wsgi_application()
