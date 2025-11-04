from django.test import TestCase

class DummyTest(TestCase):
    def test_example(self):
        """Simple test to check CI/CD pipeline"""
        self.assertEqual(1 + 1, 2)
