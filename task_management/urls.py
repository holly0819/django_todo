from django.urls import path
from . import views
from .views import SignUp

urlpatterns = [
  path('', views.task_list, name='task_list'),
  path('accounts/signup', SignUp.as_view(), name='signup')
]