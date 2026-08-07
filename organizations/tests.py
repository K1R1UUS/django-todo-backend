from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Branch, Department, Profile


class OrganizationStructureTestSetup(APITestCase):
    """Общий сетап: два филиала, по два отдела, начальники, сотрудники."""

    def setUp(self):
        self.admin = User.objects.create_superuser(username="admin", password="pass12345")

        self.ivanov = User.objects.create_user(username="ivanov", password="pass12345")
        self.petrov = User.objects.create_user(username="petrov", password="pass12345")
        self.sidorova = User.objects.create_user(username="sidorova", password="pass12345")
        self.kuznetsov = User.objects.create_user(username="kuznetsov", password="pass12345")
        self.vasilieva = User.objects.create_user(username="vasilieva", password="pass12345")

        self.moscow = Branch.objects.create(name="Москва", head=self.ivanov)
        self.kazan = Branch.objects.create(name="Казань", head=self.petrov)

        self.sales = Department.objects.create(name="Продажи", branch=self.moscow, head=self.sidorova)
        self.support = Department.objects.create(name="Поддержка", branch=self.moscow, head=self.kuznetsov)
        self.logistics = Department.objects.create(name="Логистика", branch=self.kazan)

        Profile.objects.create(user=self.vasilieva, department=self.support)


class BranchStructurePermissionTests(OrganizationStructureTestSetup):
    def test_admin_can_view_any_branch(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f"/api/branches/{self.moscow.id}/structure/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_branch_head_can_view_own_branch(self):
        self.client.force_authenticate(user=self.ivanov)
        response = self.client.get(f"/api/branches/{self.moscow.id}/structure/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_branch_head_cannot_view_foreign_branch(self):
        self.client.force_authenticate(user=self.ivanov)
        response = self.client.get(f"/api/branches/{self.kazan.id}/structure/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_department_head_cannot_view_branch_structure(self):
        """Ключевой тест: начальник отдела не поднимается до уровня филиала."""
        self.client.force_authenticate(user=self.sidorova)
        response = self.client.get(f"/api/branches/{self.moscow.id}/structure/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_employee_cannot_view_branch_structure(self):
        self.client.force_authenticate(user=self.vasilieva)
        response = self.client.get(f"/api/branches/{self.moscow.id}/structure/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_cannot_view_branch_structure(self):
        response = self.client.get(f"/api/branches/{self.moscow.id}/structure/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class DepartmentStructurePermissionTests(OrganizationStructureTestSetup):
    def test_admin_can_view_any_department(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f"/api/departments/{self.sales.id}/structure/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_department_head_can_view_own_department(self):
        self.client.force_authenticate(user=self.sidorova)
        response = self.client.get(f"/api/departments/{self.sales.id}/structure/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_department_head_cannot_view_other_department_same_branch(self):
        self.client.force_authenticate(user=self.sidorova)
        response = self.client.get(f"/api/departments/{self.support.id}/structure/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_branch_head_can_view_department_in_own_branch(self):
        """Начальник филиала имеет доступ к отделам внутри своего филиала."""
        self.client.force_authenticate(user=self.ivanov)
        response = self.client.get(f"/api/departments/{self.sales.id}/structure/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_branch_head_cannot_view_department_in_foreign_branch(self):
        self.client.force_authenticate(user=self.ivanov)
        response = self.client.get(f"/api/departments/{self.logistics.id}/structure/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_employee_cannot_view_department_structure(self):
        self.client.force_authenticate(user=self.vasilieva)
        response = self.client.get(f"/api/departments/{self.support.id}/structure/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class BranchListPermissionTests(OrganizationStructureTestSetup):
    def test_admin_can_list_all_branches(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/branches/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_branch_head_cannot_list_all_branches(self):
        self.client.force_authenticate(user=self.ivanov)
        response = self.client.get("/api/branches/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_employee_cannot_list_branches(self):
        self.client.force_authenticate(user=self.vasilieva)
        response = self.client.get("/api/branches/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)