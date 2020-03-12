from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from task_management.models import List

# Create your tests here.
class TestListViews(TestCase):
  @classmethod
  def setUpTestData(cls):
    User.objects.create_user('user', password='password')
    User.objects.create_user('other_user', password='password')

  def setUp(self):
    self.user = User.objects.get(username='user')
    self.other_user = User.objects.get(username='other_user')
    self.client = Client()
    self.client.logout()

class TestListList(TestListViews):

  def setUp(self):
    super().setUp()

    self.user.list_set.create(name='userのリスト')

  def test_redirect_to_sign_in_page_when_not_authenticated(self):

    response = self.client.get(reverse('task_list'))
    self.assertEqual(response.status_code, 302)
    self.assertEqual(response.url, "%s?next=%s" % (reverse('signin'),
                                                   reverse('task_list')))


  def test_can_access_list_list_when_authenticated(self):
    # テストではcsrf_tokenのチェックは行わない（デフォルト）
    response = self.client.post(reverse('signin'), {'username': 'user',
                                                    'password': 'password'})
    self.assertEqual(response.status_code, 302)
    self.assertEqual(response.url, reverse('task_list'))

    response = self.client.get('/')
    self.assertEqual(response.status_code, 200)

    self.assertTrue('userのリスト' in response.content.decode())

    # 他のユーザのリストを見ることはできない
    self.client.logout()
    self.client.force_login(self.other_user)
    response = self.client.get('/')
    self.assertFalse('userのリスト' in response.content.decode())

class TestAddList(TestListViews):
  def test_redirect_to_sign_in_page_when_add_list_with_not_authenticated(self):

    before_count = List.objects.count()

    response = self.client.post(reverse('add_list'), {'name': 'リスト1'})

    after_count = List.objects.count()
    self.assertEqual(after_count - before_count, 0)

    self.assertEqual(response.status_code, 302)
    self.assertEqual(response.url, "%s?next=%s" % (reverse('signin'),
                                                   reverse('add_list')))

  def test_add_list(self):
    self.client.force_login(self.user)

    before_count = List.objects.count()

    response = self.client.post(reverse('add_list'), {'name': 'リスト1'})
    after_count = List.objects.count()
    self.assertEqual(after_count - before_count, 1)

    # 異なるユーザのlist_setには、作ったlistが含まれていない
    list = List.objects.get(name='リスト1')
    self.assertTrue(list in self.user.list_set.all())
    self.assertFalse(list in self.other_user.list_set.all())

    self.assertEqual(response.status_code, 200)

class EditListViews(TestListViews):

  def setUp(self):
    super().setUp()

    self.before_name = '改名前のリスト'
    self.after_name = '改名後のリスト'
    self.list = List.objects.create(name=self.before_name, user=self.user)

  def test_redirect_to_sign_in_page_when_list_edit_not_authenticated(self):
    
    response = self.client.post(reverse('edit_list', kwargs={'pk':self.list.pk}),
                                        {'name':self.after_name})
    self.assertEqual(response.status_code, 302)
    self.assertEqual(response.url,
                     "%s?next=%s"
                      % (reverse('signin'),
                          reverse('edit_list', kwargs={'pk':self.list.pk})))
    self.assertEqual(self.list.name, self.before_name)

  def test_edit_list(self):
    self.client.force_login(self.user)
    
    response = self.client.post(reverse('edit_list', kwargs={'pk':self.list.pk}),
                                        {'name':self.after_name})
    self.assertEqual(response.status_code, 200)

    self.list.refresh_from_db()
    self.assertEqual(self.list.name, self.after_name)

  #edit -> 作ったユーザと違うユーザを見分ける
  def test_user_can_not_edit_other_users_list(self):
    self.client.force_login(self.other_user)

    response = self.client.post(reverse('edit_list', kwargs={'pk':self.list.pk}),
                                        {'name':self.after_name})
    self.list.refresh_from_db()
    self.assertEqual(self.list.name, self.before_name)

class RemoveListViews(TestListViews):

  def setUp(self):
    super().setUp()

    for i in range(1, 6):
      self.user.list_set.create(name="userのリスト%s" % i)

    self.list = self.user.list_set.all()[2]

    self.url = reverse('remove_list', kwargs={'pk':self.list.pk})

  def test_redirect_when_not_authenticated(self):
    before_count = List.objects.count()

    response = self.client.post(self.url)
    self.assertEqual(response.status_code, 302)
    self.assertEqual(response.url, "%s?next=%s" % (reverse('signin'), self.url))

    after_count = List.objects.count()
    self.assertEqual(after_count - before_count, 0)

  def test_remove_success(self):

    previous_lists = self.user.list_set.filter(sort__lt=self.list.sort)
    following_lists = self.user.list_set.filter(sort__gt=self.list.sort)

    before_sort_previous = [list.sort for list in previous_lists]
    before_sort_following = [list.sort for list in following_lists]

    before_count = List.objects.count()

    self.client.force_login(self.user)
    response = self.client.post(self.url)
    self.assertEqual(response.status_code, 200)
    
    after_count = List.objects.count()
    self.assertEqual(after_count - before_count, -1)


    # 削除したリストより後ろのリストはソート番号が１ずつ減る
    for (list, sort) in zip(previous_lists, before_sort_previous):
      list.refresh_from_db()
      self.assertEqual(list.sort, sort)

    for (list, sort) in zip(following_lists, before_sort_following):
      list.refresh_from_db()
      self.assertEqual(list.sort, sort - 1)

  def test_user_can_not_remove_other_user_list(self):
    before_count = List.objects.count()
    
    self.client.force_login(self.other_user)
    response = self.client.post(self.url)
    self.assertEqual(response.status_code, 200)

    after_count = List.objects.count()
    self.assertEqual(after_count - before_count, 0)


class SortListViews(TestListViews):

  def setUp(self):
    super().setUp()

    self.url = reverse('sort_list')

    for i in range(1, 6):
      self.user.list_set.create(name="userのリスト%s" % i)

    self.list = self.user.list_set.all()[1]

  def test_redirect_when_not_authenticated(self):
    response = self.client.post(self.url, {'pk':self.list.pk, 'sort_number':3})
    self.assertEqual(response.status_code, 302)
    self.assertEqual(response.url, "%s?next=%s" % (reverse('signin'), self.url))

  def test_sort_list_from_top_to_bottom(self):
    self.client.force_login(self.user)

    response = self.client.post(self.url, {'pk':self.list.pk, 'sort_number':3})
    self.assertEqual(response.status_code, 200)

    lists = zip(['1','3','4','2','5'], self.user.list_set.order_by('sort'))
    for (n, list) in lists:
      self.assertEqual('userのリスト%s' % n, list.name)

  def test_sort_list_from_bottom_to_top(self):
    self.client.force_login(self.user)

    response = self.client.post(self.url, {'pk':self.list.pk, 'sort_number':0})
    self.assertEqual(response.status_code, 200)

    lists = zip(['2','1','3','4','5'], self.user.list_set.order_by('sort'))
    for (n, list) in lists:
      self.assertEqual('userのリスト%s' % n, list.name)

  def test_user_can_not_sort_other_user_list(self):

    self.client.force_login(self.other_user)

    response = self.client.post(self.url, {'pk':self.list.pk, 'sort_number':3})
    self.assertEqual(response.status_code, 200)

    lists = zip(['1','2','3','4','5'], self.user.list_set.order_by('sort'))
    for (n, list) in lists:
      self.assertEqual('userのリスト%s' % n, list.name)

class TestAccount(TestCase):
  def setUp(self):
    self.user = User.objects.create_user(username='user', password='password')

    self.client = Client()
    self.client.logout()
    
    self.signup_url = reverse('signup')
    self.signin_url = reverse('signin')
    self.task_list_url = reverse('task_list')

  def test_redirect_task_list_when_authenticated(self):
    self.client.force_login(self.user)

    response = self.client.get(self.signup_url)
    self.assertEqual(response.status_code, 302)
    self.assertEqual(response.url, self.task_list_url)

    response = self.client.get(self.signin_url)
    self.assertEqual(response.status_code, 302)
    self.assertEqual(response.url, self.task_list_url)

  def test_create_user(self):
    before_count = User.objects.count()

    response = self.client.get(self.signup_url)
    self.assertEqual(response.status_code, 200)

    response = self.client.post(self.signup_url,
                                {'username':'new_user', 'password1':'password',
                                                        'password2':'password'})
    self.assertEqual(response.status_code, 302)
    self.assertEqual(response.url, self.task_list_url)

    after_count = User.objects.count()

    self.assertEqual(after_count - before_count, 1)

  def test_login(self):
    pass    

