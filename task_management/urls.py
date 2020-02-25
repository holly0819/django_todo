from django.urls import path
from . import views

urlpatterns = [
  path('', views.task_list, name='task_list'),
  path('accounts/signup', views.SignUp.as_view(), name='signup'),
  path('accounts/signin', views.SignIn.as_view(), name='signin'),
  path('accounts/signout', views.SignOut.as_view(), name='signout'),
]