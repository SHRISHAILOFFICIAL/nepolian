from django.test import TestCase
from helping_hands import settings  

class DummyTest(TestCase):
    def test_import(self):
        """Ensure helping_hands module imports correctly"""
        self.assertTrue(hasattr(settings, 'INSTALLED_APPS'))
