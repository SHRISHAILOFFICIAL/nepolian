import os
import django
from django.conf import settings

# Configure Django settings before tests run
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helping_hand_core.settings')

def pytest_configure(config):
    """Configure pytest for Django."""
    if not settings.configured:
        django.setup()
    settings.DEBUG = False


