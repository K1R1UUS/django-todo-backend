from django.shortcuts import render, redirect
from django.http import HttpResponse

def hello_view(request):
    return HttpResponse('Hello, django PLAN-A! =)')

def task_list(request):
    return HttpResponse('Это будет твой список задач')


