from django.test import TestCase

# Create your tests here.
class TestTest(TestCase):

  def test_is_test(self):
    self.assertIs(True, True)