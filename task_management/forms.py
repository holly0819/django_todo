from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import List, Task

class SignUpForm(UserCreationForm):
  pass

class SignInForm(AuthenticationForm):
  pass

class ListForm(forms.ModelForm):
  
  class Meta:
    model = List
    fields = ('name',)
    
class TaskForm(forms.ModelForm):

  class Meta:
    model = Task
    fields = ('name', 'description', 'deadline', 'list')

  def __init__(self, *args, **kwargs):
    user = kwargs.pop('user')
    super().__init__(*args, **kwargs)
    self.fields['list'].queryset = List.objects.filter(user=user)