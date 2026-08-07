from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from tasks.models import Task
from .models import Branch, Department, Profile


class DepartmentInline(admin.TabularInline):
    """Показывает отделы прямо на странице филиала."""
    model = Department
    extra = 0
    fields = ("name", "head")


class ProfileInline(admin.TabularInline):
    """Список сотрудников, закреплённых за отделом."""
    model = Profile
    extra = 0
    fields = ("user",)
    fk_name = "department"


class TaskInline(admin.TabularInline):
    """Список задач пользователя (только просмотр)."""
    model = Task
    fk_name = "author"
    extra = 0
    fields = ("title", "status", "due_date")
    readonly_fields = ("title", "status", "due_date")
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


class ProfileInlineForUser(admin.StackedInline):
    """Отдел пользователя — прямо на его странице."""
    model = Profile
    can_delete = False
    extra = 0


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name", "head", "created_at")
    search_fields = ("name",)
    inlines = [DepartmentInline]


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "branch", "head", "created_at")
    list_filter = ("branch",)
    search_fields = ("name",)
    inlines = [ProfileInline]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "department")
    list_filter = ("department",)
    search_fields = ("user__username",)


class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInlineForUser, TaskInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)