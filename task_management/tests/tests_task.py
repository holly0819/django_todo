from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from task_management.models import List, Task

class TestTaskViews(TestCase):

  @classmethod
  def setUpTestData(cls):
    user = User.objects.create_user('user', password='password')
    for i in range(3):
      user.list_set.create(name='List ' + str(i + 1))

    other_user = User.objects.create_user('other_user', password='password')
    for i in range(3):
      other_user.list_set.create(name='List' + str(i + 1))

  def setUp(self):
    self.user = User.objects.get(username='user')
    self.other_user = User.objects.get(username='other_user')
    self.client = Client()
    self.client.logout()

class TestTaskList(TestTaskViews):
  pass