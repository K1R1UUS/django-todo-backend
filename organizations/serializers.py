from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Branch, Department, Profile


class EmployeeSerializer(serializers.ModelSerializer):
    """Краткая информация о сотруднике для вложенного списка."""
    username = serializers.CharField(source="user.username")
    email = serializers.CharField(source="user.email")

    class Meta:
        model = Profile
        fields = ["username", "email"]


class DepartmentStructureSerializer(serializers.ModelSerializer):
    """Отдел с начальником и списком сотрудников."""
    head = serializers.CharField(source="head.username", allow_null=True)
    employees = EmployeeSerializer(many=True, read_only=True)

    class Meta:
        model = Department
        fields = ["id", "name", "head", "employees"]


class BranchStructureSerializer(serializers.ModelSerializer):
    """Филиал целиком: список отделов с их начальниками и сотрудниками."""
    head = serializers.CharField(source="head.username", allow_null=True)
    departments = DepartmentStructureSerializer(many=True, read_only=True)

    class Meta:
        model = Branch
        fields = ["id", "name", "head", "departments"]