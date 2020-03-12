from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

class TaskListTests(StaticLiveServerTestCase):

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    options = Options()
    options.add_argument('--headless')
    cls.selenium = webdriver.Chrome(chrome_options=options)
    cls.selenium.implicitly_wait(10)
    caps = DesiredCapabilities.CHROME
    caps['loggingPrefs'] = {'browser': 'SEVERE'}

  @classmethod
  def tearDownClass(cls):
    cls.selenium.quit()
    super().tearDownClass()

  # liveservertestcaseにおいて、データベースはメソッドごとにリセットされるので、
  # setUpメソッドを使ってメソッドごとにデータを作る必要がある
  def setUp(self):
    self.user = User.objects.create_user(username='user', password='password')
    self.selenium.get(self.live_server_url + reverse('signout'))

  def login(self):
    # ログイン処理
    self.selenium.get(self.live_server_url + reverse('signin'))

    self.selenium.find_element_by_id("id_username").send_keys("user")
    self.selenium.find_element_by_id("id_password").send_keys("password")

    self.selenium.find_element_by_xpath(
      "/html/body/form/input[@type='submit']"
    ).click()

  def test_login(self):
    self.login()

    self.assertEqual(self.selenium.current_url,
                     self.live_server_url + reverse('task_list'))

  def test_sort_list_to_bottom(self):
    for i in range(1, 6):
      self.user.list_set.create(name='List ' + str(i))

    self.login()
    lists = self.selenium.find_element_by_xpath("//ul[@id='lists']")
    before_each_list = lists.find_elements(By.TAG_NAME, 'li')

    # 2番目の要素を4番目に移動する [1,2,3,4,5] -> [1,3,4,2,5]
    source = before_each_list[1]
    target = before_each_list[3]

    # ドラッグアンドドロップを実行する
    actions = ActionChains(self.selenium)
    actions.drag_and_drop(source, target)
    actions.perform()

    # ドラッグ後の各要素のインデックスを検証する
    after_each_list = lists.find_elements(By.TAG_NAME, 'li')
    for (list, i) in zip(after_each_list, [0,2,3,1,4]):
      self.assertEqual(list.text, 'List ' + str(i + 1))
      

    # 更新後も変わっていないか確認する
    self.selenium.refresh()

    lists = self.selenium.find_element_by_xpath("//ul[@id='lists']")
    after_each_list = lists.find_elements(By.TAG_NAME, 'li')
    for(list, i) in zip(after_each_list, [0,2,3,1,4]):
      self.assertEqual(list.text, 'List ' + str(i + 1))

  def test_sort_list_to_top(self):
    for i in range(1, 6):
      self.user.list_set.create(name='List ' + str(i))

    self.login()
    lists = self.selenium.find_element_by_xpath("//ul[@id='lists']")
    before_each_list = lists.find_elements(By.TAG_NAME, 'li')

    # 4番目の要素を3番目に移動する [1,2,3,4,5] -> [1,2,4,3,5]
    source = before_each_list[3]
    target = before_each_list[2]

    # ドラッグアンドドロップを実行する
    actions = ActionChains(self.selenium)
    # actions.click_and_hold(source).move_to_element(target).move_by_offset(10, 0).release(target)
    actions.click_and_hold(source).move_to_element_with_offset(target, 10, 0).release()
    # actions.drag_and_drop(source, target)
    actions.perform()


    # ドラッグ後の各要素のインデックスを検証する
    after_each_list = lists.find_elements(By.TAG_NAME, 'li')
    for (list, i) in zip(after_each_list, [0,1,3,2,4]):
      self.assertEqual(list.text, 'List ' + str(i + 1))
      

    # 更新後も変わっていないか確認する
    self.selenium.refresh()

    lists = self.selenium.find_element_by_xpath("//ul[@id='lists']")
    after_each_list = lists.find_elements(By.TAG_NAME, 'li')
    for(list, i) in zip(after_each_list, [0,1,3,2,4]):
      self.assertEqual(list.text, 'List ' + str(i + 1))

  def test_add_list(self):
    self.login()

    new_list_xpath = "//*[@id='lists']/li[contains(@class, 'focus')]/span[text()='新しいリスト']"
    new_tasks_title_xpath = "//*[@id='task-list']/h2[text()='新しいリスト']"
    new_list = self.selenium.find_elements_by_xpath(new_list_xpath)
    self.assertEqual(len(new_list), 0)
    new_tasks_title = self.selenium.find_elements_by_xpath(new_tasks_title_xpath)
    self.assertEqual(len(new_tasks_title), 0)

    # リスト追加する
    self.selenium.find_element_by_id("add-list-button").click()

    # モーダルが表示されるまで待つ
    WebDriverWait(self.selenium, 10).until(
      ec.visibility_of_element_located((By.ID, "add-list-modal")))

    # フォームの送信
    self.selenium.find_element_by_id("add_list_for_name").send_keys("新しいリスト")
    self.selenium.save_screenshot('test_images/before_push_button.png')
    self.selenium\
    .find_element_by_xpath("//button[@type='submit'][@form='add-list-form']")\
    .click()

    self.selenium.save_screenshot('test_images/push_button.png')
    # フォームが消えるまで待つ
    WebDriverWait(self.selenium, 10).until_not(
      ec.visibility_of_element_located((By.ID, "add-list-modal")))

    # 追加されたリストが存在するか検証する
    new_list = self.selenium.find_elements_by_xpath(new_list_xpath)
    self.assertEqual(len(new_list), 1)

    # 追加したリストのタスク一覧画面が存在するか検証する
    self.selenium.save_screenshot('test_images/after_add.png')
    list_id = new_list[0].find_element_by_xpath('./..').get_attribute("data-list-id")
    new_tasks_list_xpath =\
       "//*[@id='task-list']/*[@class='tasks'][@data-list-id='list-%s']" % str(list_id)
    new_tasks_list = self.selenium.find_elements_by_xpath(new_tasks_list_xpath)
    self.assertEqual(len(new_tasks_list), 1)

    # 作ったリストのタイトルに変更されているか検証する
    new_tasks_title = self.selenium.find_elements_by_xpath(new_tasks_title_xpath)
    self.assertEqual(len(new_tasks_title), 1)

    # リロード後も維持されているか検証する
    self.selenium.refresh()
    new_list = self.selenium.find_elements_by_xpath(new_list_xpath)
    self.assertEqual(len(new_list), 1)
    new_tasks_title = self.selenium.find_elements_by_xpath(new_tasks_title_xpath)
    self.assertEqual(len(new_tasks_title), 1)
    new_tasks_list = self.selenium.find_elements_by_xpath(new_tasks_list_xpath)
    self.assertEqual(len(new_tasks_list), 1)

  def test_remove_list(self):
    for i in range(5):
      self.user.list_set.create(name="List " + str(i + 1))

    self.login()

    # リストを削除する
    target_list = self.selenium.find_element_by_xpath(
                    "//*[@id='lists']/*[contains(@class, 'list')][2]")
    target_name = target_list.find_element_by_xpath(
                    "./*[@class='list-name']").text
    remove_button = target_list.find_element_by_xpath(
                      "./*[@class='list-edit-buttons']\
                        /*[contains(@class, 'remove-list-button')]")
    action = ActionChains(self.selenium)
    action.move_to_element(target_list)\
          .move_to_element(remove_button).click().perform()
    self.selenium.find_element_by_xpath(
      "//*[@id='remove-list-modal']//button[@form='remove-list-form']").click()
    sleep(3) # アニメーション完了待ち

    # 削除されたリストが消えたか検証する
    target_list = self.selenium.find_elements_by_xpath(
      "//*[@id='lists']/li/span[@class='list-name'][text()='%s']" % target_name
    )
    self.assertEqual(len(target_list), 0)

    # リロードしても消えたままか確認する
    self.selenium.refresh()
    target_list = self.selenium.find_elements_by_xpath(
      "//*[@id='lists']/li/span[@class='list-name'][text()='%s']" % target_name
    )
    self.assertEqual(len(target_list), 0)

  def test_edit_list(self):
    for i in range(5):
      self.user.list_set.create(name="List " + str(i))

    self.login()

    # リストを更新する
    target_list = self.selenium.find_element_by_xpath(
      "//ul[@id='lists']/li[3]")
    before_name = target_list.find_element_by_xpath(
      "./*[@class='list-name']").text
    edit_button = target_list.find_element_by_xpath(
      "./*[@class='list-edit-buttons']/*[contains(@class, 'edit-list-button')]")

    action = ActionChains(self.selenium)
    action.move_to_element(target_list)\
          .move_to_element(edit_button).click().perform()

    sleep(1)

    self.selenium.save_screenshot('test_images/test.png')
    # 編集モーダルの名前フィールドがないので、原因を探ろう
    input_field = self.selenium.find_element_by_xpath(
      "//*[@id='edit-list-modal']//input[@id='edit_list_for_name']")
    input_field.clear()
    input_field.send_keys('新しい名前')

    self.selenium.find_element_by_xpath(
      "//*[@id='edit-list-modal']//button[@form='edit-list-form']").click()
    sleep(3)
    # リスト名が変わっているか検証する
    before_list = self.selenium.find_elements_by_xpath(
      "//ul[@id='lists']/li/*[@class='list-name'][text()='%s']" % before_name)
    after_list = self.selenium.find_elements_by_xpath(
      "//ul[@id='lists']/li/*[@class='list-name'][text()='新しい名前']")

    self.assertEqual(len(before_list), 0)
    self.assertEqual(len(after_list), 1)

    # リロードしても変更後のままか検証する
    self.selenium.refresh()
    before_list = self.selenium.find_elements_by_xpath(
      "//ul[@id='lists']/li/*[@class='list-name'][text()='%s']" % before_name)
    after_list = self.selenium.find_elements_by_xpath(
      "//ul[@id='lists']/li/*[@class='list-name'][text()='新しい名前']")

    self.assertEqual(len(before_list), 0)
    self.assertEqual(len(after_list), 1)

  def test_switch_lists(self):
    for i in range(1, 6):
      self.user.list_set.create(name='List ' + str(i))

    self.login()

    # Cookieにinitial_list_idがない場合、pkを昇順に並べて一番最初のリストが自動でフォーカスされる
    lists = self.selenium.find_elements_by_xpath(
      "//ul[@id='lists']/li[contains(@class, 'focus')\
                            and contains(@class, 'list')]/span[text()='List 1']")
    self.assertEqual(len(lists), 1)

    # クリックされたリストがフォーカスされる（上から3番目）
    self.selenium.find_element_by_xpath(
      "//ul[@id='lists']/li[contains(@class, 'list')][3]").click()
    before_lists = self.selenium.find_elements_by_xpath(
      "//ul[@id='lists']/li[contains(@class, 'focus')]/span[text()='List 1']")
    after_lists = self.selenium.find_elements_by_xpath(
      "//ul[@id='lists']/li[contains(@class, 'focus')]/span[text()='List 3']")
    self.assertEqual(len(before_lists), 0)
    self.assertEqual(len(after_lists), 1)

    # 更新後もフォーカスが維持されている
    self.selenium.refresh()
    before_lists = self.selenium.find_elements_by_xpath("//ul[@id='lists']/li[contains(@class, 'focus')]/span[text()='List 1']")
    after_lists = self.selenium.find_elements_by_xpath("//ul[@id='lists']/li[contains(@class, 'focus')]/span[text()='List 3']")
    self.assertEqual(len(before_lists), 0)
    self.assertEqual(len(after_lists), 1)

  def test_switch_lists_when_remove_bottom_focused_list(self):
    for i in range(1,6):
      self.user.list_set.create(name='List ' + str(i))

    self.login()

    # 3番目のリストをクリックしてフォーカスさせる
    self.selenium.find_element_by_xpath(
      "//ul[@id='lists']/li[contains(@class, 'list')][3]").click()
    lists = self.selenium.find_elements_by_xpath(
      "//ul[@id='lists']/li[contains(@class, 'focus') and contains(@class, 'list')]\
        [1]/span[text()='List 3']/..")
    self.assertEqual(len(lists), 1)
  
    # フォーカスされているリスト以外のタスクは表示されていないことを確認する
    target_id = lists[0].get_attribute('data-list-id')
    tasks_list = self.selenium.find_elements_by_xpath(
      "//*[@id='task-list']/*[@class='tasks']")

    for elem in tasks_list:
      if elem.get_attribute('data-list-id') == "list-%s" % target_id:
        self.assertTrue(elem.is_displayed())
      else:
        self.assertFalse(elem.is_displayed())

    # 2番目以降でフォーカスされているリストを削除したとき、フォーカスが上のリストに移る
    remove_button = lists[0].find_element_by_xpath(
                      ".//*[contains(@class, 'remove-list-button')]")
    action = ActionChains(self.selenium)
    action.move_to_element(lists[0])\
          .move_to_element(remove_button).click().perform()
    # 削除用のモーダルが表示されるまで待つ
    WebDriverWait(self.selenium, 10).until(
      ec.visibility_of_element_located((By.ID, "remove-list-modal")))
    self.selenium.find_element_by_xpath("//*[@id='remove-list-modal']\
                                         //button[@form='remove-list-form']")\
                                        .click()
    # 削除用のモーダルが消えるまで待つ
    WebDriverWait(self.selenium, 10).until_not(
      ec.visibility_of_element_located((By.ID, "remove-list-modal")))
    
    # フォーカスの対象が変わっているのを検証する
    lists = self.selenium.find_elements_by_xpath(
      "//ul[@id='lists']/li[contains(@class, 'focus') and contains(@class, 'list')]\
       /span[text()='List 3']/..")
    self.assertEqual(len(lists), 0)
    lists = self.selenium.find_elements_by_xpath(
      "//ul[@id='lists']/li[contains(@class, 'focus') and contains(@class, 'list')]\
       /span[text()='List 2']/..")
    self.assertEqual(len(lists), 1)

    # 変更後のリストのタスクが表示されていることを検証する
    target_id = lists[0].get_attribute('data-list-id')
    tasks_list = self.selenium.find_elements_by_xpath(
      "//*[@id='task-list']/*[@class='tasks']")
    for elem in tasks_list:
      if elem.get_attribute('data-list-id') == "list-%s" % target_id:
        self.assertTrue(elem.is_displayed())
      else:
        self.assertFalse(elem.is_displayed())

  def test_switch_lists_when_remove_top_focused_list(self):
    for i in range(1,6):
      self.user.list_set.create(name='List ' + str(i))

    self.login()

    # 最初にフォーカスされているリストを確認する
    lists = self.selenium.find_elements_by_xpath(
      "//ul[@id='lists']/li[contains(@class, 'focus') and contains(@class, 'list')]\
        [1]/span[text()='List 1']/..")
    self.assertEqual(len(lists), 1)
    target_id = lists[0].get_attribute('data-list-id')
    tasks_list = self.selenium.find_elements_by_xpath(
      "//*[@id='task-list']/*[@class='tasks']")

    # フォーカスされているリスト以外のタスクは表示されていないことを確認する
    for elem in tasks_list:
      if elem.get_attribute('data-list-id') == "list-%s" % target_id:
        self.assertTrue(elem.is_displayed())
      else:
        self.assertFalse(elem.is_displayed())

    # 1番上のフォーカスされているリストを削除したとき、フォーカスが下のリストに移る
    remove_button = lists[0].find_element_by_xpath(
                      ".//*[contains(@class, 'remove-list-button')]")
    action = ActionChains(self.selenium)
    action.move_to_element(lists[0])\
          .move_to_element(remove_button).click().perform()
    # 削除用のモーダルが表示されるまで待つ
    WebDriverWait(self.selenium, 10).until(
      ec.visibility_of_element_located((By.ID, "remove-list-modal")))
    self.selenium.find_element_by_xpath("//*[@id='remove-list-modal']\
                                          //button[@form='remove-list-form']")\
                                        .click()
    # 削除用のモーダルが消えるまで待つ
    WebDriverWait(self.selenium, 10).until_not(
      ec.visibility_of_element_located((By.ID, "remove-list-modal")))
    
    # フォーカスの対象が変わっているのを検証する
    lists = self.selenium.find_elements_by_xpath(
      "//ul[@id='lists']/li[contains(@class, 'focus') and contains(@class, 'list')]\
        /span[text()='List 1']/..")
    self.assertEqual(len(lists), 0)
    lists = self.selenium.find_elements_by_xpath(
      "//ul[@id='lists']/li[contains(@class, 'focus') and contains(@class, 'list')]\
        /span[text()='List 2']/..")
    self.assertEqual(len(lists), 1)

    # 変更後のリストのタスクが表示されていることを検証する
    target_id = lists[0].get_attribute('data-list-id')
    tasks_list = self.selenium.find_elements_by_xpath(
      "//*[@id='task-list']/*[@class='tasks']")
    for elem in tasks_list:
      if elem.get_attribute('data-list-id') == "list-%s" % target_id:
        self.assertTrue(elem.is_displayed())
      else:
        self.assertFalse(elem.is_displayed())
