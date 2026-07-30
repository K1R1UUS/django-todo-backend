from rest_framework.permissions import BasePermission


class IsBranchHeadOrAdmin(BasePermission):
    """Доступ к структуре филиала: admin/staff — всегда, иначе только начальник этого филиала."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_staff or user.is_superuser:
            return True
        return obj.head_id == user.id


class IsDepartmentOrBranchHeadOrAdmin(BasePermission):
    """Доступ к структуре отдела: admin/staff, начальник этого отдела, или начальник филиала-владельца."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_staff or user.is_superuser:
            return True
        if obj.head_id == user.id:
            return True
        return obj.branch.head_id == user.id