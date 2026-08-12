from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .forms import TaskForm
from .permissions import get_visible_tasks


@login_required
def task_list_view(request):
    tasks = get_visible_tasks(request.user).select_related("assignee", "department", "branch")
    status_filter = request.GET.get("status")
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    return render(request, "tasks/task_list.html", {"tasks": tasks, "status_filter": status_filter})

def _task_form_context(form, is_edit, task=None):
    return {
        "form": form,
        "is_edit": is_edit,
        "task": task,
        "department_branch_map": form.department_branch_map,
        "assignee_department_map": form.assignee_department_map,
        "show_branch": form.show_branch,
        "show_department": form.show_department,
    }

@login_required
def task_create_view(request):
    if request.method == "POST":
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.author = request.user
            task.save()
            messages.success(request, "Задача создана.")
            return redirect("web-task-list")
    else:
        form = TaskForm(user=request.user)
    return render(request, "tasks/task_form.html", _task_form_context(form, is_edit=False))



@login_required
def task_edit_view(request, pk):
    task = get_object_or_404(get_visible_tasks(request.user), pk=pk)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Задача обновлена.")
            return redirect("web-task-list")
    else:
        form = TaskForm(instance=task, user=request.user)
    return render(request, "tasks/task_form.html", _task_form_context(form, is_edit=True, task=task))


@login_required
def task_delete_view(request, pk):
    task = get_object_or_404(get_visible_tasks(request.user), pk=pk)
    if not (request.user.is_staff or request.user.is_superuser or task.author_id == request.user.id):
        messages.error(request, "У вас нет прав на удаление этой задачи.")
        return redirect("web-task-list")
    if request.method == "POST":
        task.delete()
        messages.success(request, "Задача удалена.")
    return redirect("web-task-list")


@login_required
def profile_view(request):
    user = request.user
    if request.method == "POST":
        if "update_email" in request.POST:
            user.email = request.POST.get("email", "").strip()
            user.save()
            messages.success(request, "Email обновлён.")
        elif "change_password" in request.POST:
            old_password = request.POST.get("old_password")
            new_password = request.POST.get("new_password")
            if not user.check_password(old_password):
                messages.error(request, "Неверный текущий пароль.")
            else:
                try:
                    validate_password(new_password, user=user)
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, "Пароль изменён.")
                except ValidationError as e:
                    for err in e.messages:
                        messages.error(request, err)
        return redirect("web-profile")

    task_count = get_visible_tasks(user).filter(author=user).count()
    return render(request, "tasks/profile.html", {"task_count": task_count})