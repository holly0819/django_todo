from django.contrib.auth import login
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from .forms import SignUpForm, SignInForm

# ユーザ管理

class SignUp(CreateView):
  form_class = SignUpForm
  template_name = 'accounts/signup.html'
  success_url = reverse_lazy('task_list')

  def form_valid(self, form):
    user = form.save()
    login(self.request, user)
    self.object = user
    return HttpResponseRedirect(self.get_success_url()) # リダイレクト

class SignIn(LoginView):
  form_class = SignInForm
  template_name = 'accounts/signin.html'

class SignOut(LogoutView):
  pass
# ユーザ管理

# Create your views here.
def task_list(request):
  return render(request, 'task_management/task_list.html', {})