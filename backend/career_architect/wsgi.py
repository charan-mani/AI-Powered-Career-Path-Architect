"""
WSGI config for career_architect project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'career_architect.settings')

application = get_wsgi_application()