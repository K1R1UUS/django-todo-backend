from django import forms
from django.contrib.auth.models import User
from organizations.models import Branch, Department, Profile
from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "status", "due_date", "branch", "department", "assignee"]
        widgets = {
            "due_date": forms.DateTimeInput(attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
            "description": forms.Textarea(attrs={"rows": 4}),
        }
        labels = {
            "branch": "Филиал",
            "department": "Отдел",
            "assignee": "Сотрудник",
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        for name in ("branch", "department", "assignee"):
            self.fields[name].required = False
            self.fields[name].empty_label = "—"

        self.department_branch_map = {}
        self.assignee_department_map = {}
        self.show_branch = True
        self.show_department = True

        if user.is_staff or user.is_superuser:
            all_departments = Department.objects.all()
            self.department_branch_map = {d.id: d.branch_id for d in all_departments}
            employees = Profile.objects.filter(department__isnull=False)
            self.assignee_department_map = {e.user_id: e.department_id for e in employees}
            return

        if hasattr(user, "headed_branch"):
            branch = user.headed_branch
            self.fields["branch"].queryset = Branch.objects.filter(id=branch.id)
            self.fields["branch"].widget = forms.HiddenInput()
            self.fields["branch"].initial = branch.id
            self.show_branch = False

            departments = Department.objects.filter(branch=branch)
            self.fields["department"].queryset = departments
            self.department_branch_map = {d.id: d.branch_id for d in departments}

            heads = departments.filter(head__isnull=False)
            self.fields["assignee"].queryset = User.objects.filter(id__in=heads.values_list("head_id", flat=True))
            self.assignee_department_map = {d.head_id: d.id for d in heads}

        elif hasattr(user, "headed_department"):
            own_department = user.headed_department

            self.fields["branch"].widget = forms.HiddenInput()
            self.show_branch = False

            self.fields["department"].queryset = Department.objects.filter(id=own_department.id)
            self.fields["department"].widget = forms.HiddenInput()
            self.fields["department"].initial = own_department.id
            self.show_department = False
            self.department_branch_map = {own_department.id: own_department.branch_id}

            employees = Profile.objects.filter(department=own_department)
            self.fields["assignee"].queryset = User.objects.filter(id__in=employees.values_list("user_id", flat=True))
            self.assignee_department_map = {e.user_id: own_department.id for e in employees}

        else:
            self.fields["branch"].queryset = Branch.objects.none()
            self.fields["department"].queryset = Department.objects.none()
            self.fields["assignee"].queryset = User.objects.none()
            self.fields["branch"].widget = forms.HiddenInput()
            self.fields["department"].widget = forms.HiddenInput()
            self.fields["assignee"].widget = forms.HiddenInput()
            self.show_branch = False
            self.show_department = False