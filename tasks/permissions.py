from rest_framework.permissions import BasePermission


def get_user_department(user):
    """Отдел пользователя, если у него есть Profile."""
    profile = getattr(user, "profile", None)
    return profile.department if profile else None


def is_department_head(user, department):
    """Является ли user начальником именно этого отдела."""
    return department is not None and department.head_id == user.id


def is_branch_head(user, branch):
    """Является ли user начальником именно этого филиала."""
    return branch is not None and branch.head_id == user.id


class CanAssignTaskTarget(BasePermission):
    """
    Проверяет, что пользователь имеет право адресовать задачу
    указанным branch/department/assignee.
    """

    def has_permission(self, request, view):
        if request.method not in ("POST", "PUT", "PATCH"):
            return True

        user = request.user
        if user.is_staff or user.is_superuser:
            return True

        branch_id = request.data.get("branch")
        department_id = request.data.get("department")
        assignee_id = request.data.get("assignee")

        if not branch_id and not department_id and not assignee_id:
            return True

        user_department = get_user_department(user)

        if user_department and is_department_head(user, user_department):
            if branch_id:
                return False
            if department_id and str(user_department.id) != str(department_id):
                return False
            if assignee_id:
                from organizations.models import Profile
                assignee_dept = Profile.objects.filter(user_id=assignee_id).values_list(
                    "department_id", flat=True
                ).first()
                if str(assignee_dept) != str(user_department.id):
                    return False
            return True

        if hasattr(user, "headed_branch"):
            own_branch = user.headed_branch
            if branch_id and str(own_branch.id) != str(branch_id):
                return False
            if department_id:
                from organizations.models import Department
                dept = Department.objects.filter(id=department_id).first()
                if not dept or dept.branch_id != own_branch.id:
                    return False
            if assignee_id:
                from organizations.models import Department
                target_is_dept_head = Department.objects.filter(
                    branch=own_branch, head_id=assignee_id
                ).exists()
                if not target_is_dept_head:
                    return False
            return True

        return False