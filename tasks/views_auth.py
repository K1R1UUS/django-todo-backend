from django.shortcuts import render
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.contrib.auth import logout as django_logout


@csrf_protect
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect("/api/tasks/")
        else:
            return render(request, "login.html", {"error": "Неверный логин или пароль"})
    return render(request, "login.html")


def logout_view(request):
    django_logout(request)
    return HttpResponseRedirect("/api/auth/login/")