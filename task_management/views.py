from django.shortcuts import render
from django.http import HttpResponsegi

# Create your views here.
def task_list(request):
  return HttpResponse('Hello Django');