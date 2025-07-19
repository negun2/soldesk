# onpremweb/onprem_project_config/wsgi.py
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onprem_project_config.settings')

application = get_wsgi_application()
