from django.urls import path
from . import views

urlpatterns = [
  path('', views.task_list, name='task_list'),
  path('accounts/signup', views.SignUp.as_view(), name='signup'),
  path('accounts/signin', views.SignIn.as_view(), name='signin'),
  path('accounts/signout', views.SignOut.as_view(), name='signout'),
  path('list/add', views.AddList, name='add_list'),
  path('list/<int:pk>/edit', views.EditList, name='edit_list'),
  path('list/<int:pk>/remove', views.RemoveList, name='remove_list'),
  path('list/sort', views.SortList, name='sort_list'),
  path('task/add', views.AddTask, name='add_task')
]