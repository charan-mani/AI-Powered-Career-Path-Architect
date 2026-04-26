import os
import sys
import pytest
from django.conf import settings

# Add the backend directory to Python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

@pytest.fixture(scope='session')
def django_db_setup():
    """Configure database for tests"""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'ATOMIC_REQUESTS': True,  # Add this line
    }