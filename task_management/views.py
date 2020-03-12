from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponse, HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView
from .forms import SignUpForm, SignInForm, ListForm, TaskForm
from .models import List

# ユーザ管理

class SignUp(CreateView):
  form_class = SignUpForm
  template_name = 'accounts/signup.html'
  success_url = reverse_lazy('task_list')

  def get(self, request, *args, **kwargs):
    # ログイン済みの場合、LOGIN_REDIRECT_URLへ遷移する
    # https://stackoverflow.com/questions/47879319/custom-loginview-in-django-2
    if self.request.user.is_authenticated:
      return redirect(settings.LOGIN_REDIRECT_URL)

    return super(SignUp, self).get(request, *args, **kwargs)

  def form_valid(self, form):
    user = form.save()
    login(self.request, user)
    self.object = user
    return HttpResponseRedirect(self.get_success_url()) # リダイレクト

class SignIn(LoginView):
  template_name = 'accounts/signin.html'

  def get(self, request, *args, **kwargs):
    # ログイン済みの場合、LOGIN_REDIRECT_URLへ遷移する
    # https://stackoverflow.com/questions/47879319/custom-loginview-in-django-2
    if self.request.user.is_authenticated:
      return redirect(settings.LOGIN_REDIRECT_URL)

    return super(SignIn, self).get(request, *args, **kwargs)

class SignOut(LogoutView):
  def dispatch(self, request, *args, **kwargs):
    response = super().dispatch(request, *args, **kwargs)
    response.delete_cookie('initial_list_id')
    return response

# ユーザ管理

# Create your views here.
@login_required
def task_list(request):
  user = User.objects.get(pk=request.user.id)
  lists = user.list_set.order_by('sort')
  # html要素のidの重複を避けるため、auto_idでそれぞれ別の形にする
  add_list_form = ListForm(auto_id='add_list_for_%s')
  edit_list_form = ListForm(auto_id='edit_list_for_%s')
  add_task_form = TaskForm(auto_id='add_task_for_%s', user=request.user)
  initial_list_id = request.COOKIES.get('initial_list_id')\
                     or user.list_set.first().pk if user.list_set.first() else None
  return render(request, 'task_management/task_list.html',
                {'lists':lists, 'add_list_form':add_list_form,
                 'edit_list_form':edit_list_form,  'add_task_form': add_task_form,
                 'initial_list_id': initial_list_id})

@login_required
def AddList(request):
  form = ListForm(request.POST)
  if form.is_valid():
    list = form.save(commit=False)
    list.user = request.user
    list.save()

    form = ListForm()
    list_item = render_to_string('task_management/list.html', { 'list':list })
    list_form = render_to_string('task_management/list_form.html',
                                 {'form':form}, request)
    each_list = render_to_string('task_management/tasks_each_list.html', {'list':list })
    list_id = list.id
  else:
    return HttpResponse(status=400)
  data = {'list_item':list_item, 'list_form':list_form,
          'each_list':each_list, 'list_id': list.id}
  return JsonResponse(data)

@login_required
def EditList(request, pk):
  list = get_object_or_404(List, pk=pk)
  form = ListForm(request.POST, instance=list)
  if form.is_valid and request.user == list.user:
    form.save()

  data = {'name':list.name, 'pk':list.pk}
  return JsonResponse(data)

@login_required
def RemoveList(request, pk):
  list = get_object_or_404(List, pk=pk)
  if request.user == list.user:
    lists = List.objects.filter(sort__gt=list.sort, user=request.user)
    for li in lists:
      li.sort -= 1
      li.save()
    list.delete()
  return HttpResponse(pk)
  # リストの持ち主がユーザのものか確認する

@login_required
def SortList(request):
  pk = int(request.POST['pk'])
  sort_number = int(request.POST['sort_number'])
  list = get_object_or_404(List, pk=pk)
  if request.user == list.user:
    # リストを上に上げる（=ソート番号が小さくなる）
    if list.sort > sort_number:
      lists = List.objects.filter(sort__range=(sort_number, list.sort - 1), user=request.user)
      for li in lists:
        li.sort += 1
        li.save()
    # リストを下に下げる(=ソート番号が大きくなる)
    elif list.sort < sort_number:
      lists = List.objects.filter(sort__range=(list.sort + 1, sort_number), user=request.user)
      for li in lists:
        li.sort -= 1
        li.save()
    list.sort = sort_number
    list.save()

  return HttpResponse(status=200)

@login_required
def AddTask(request):
  pass