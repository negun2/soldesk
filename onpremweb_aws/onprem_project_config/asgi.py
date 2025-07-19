# onpremweb/onprem_project_config/asgi.py
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onprem_project_config.settings')

application = get_asgi_application()
