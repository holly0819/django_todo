from django.contrib.auth import login
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.shortcuts import render
from django.views.generic.edit import CreateView
from .forms import SignUpForm

# ユーザ管理

class SignUp(CreateView):
  form_class = SignUpForm
  template_name = 'accounts/signup.html'
  success_url = reverse_lazy('')

  def form_valid(self, form):
    user = form.save()
    login(self.request, user)
    self.object = user
    return HttpResponseRedirect(self.get_success_url()) # リダイレクト
# ユーザ管理

# Create your views here.
def task_list(request):
  return HttpResponse('Hello Django');