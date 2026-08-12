from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Task
from django.urls import reverse
from django.test import TestCase
from organizations.models import Branch, Department, Profile


class TaskModelTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pass12345")

    def test_str_returns_title(self):
        task = Task.objects.create(title="Купить молоко", author=self.user)
        self.assertEqual(str(task), "Купить молоко")

    def test_default_status_is_todo(self):
        task = Task.objects.create(title="Тест", author=self.user)
        self.assertEqual(task.status, "todo")

    def test_ordering_is_newest_first(self):
        t1 = Task.objects.create(title="Первая", author=self.user)
        t2 = Task.objects.create(title="Вторая", author=self.user)
        tasks = list(Task.objects.all())
        self.assertEqual(tasks[0], t2)
        self.assertEqual(tasks[1], t1)


class TaskPermissionsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pass12345")
        self.url = "/api/tasks/"

    def test_anonymous_user_cannot_list_tasks(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_user_cannot_create_task(self):
        response = self.client.post(self.url, {"title": "Задача"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TaskIsolationTests(APITestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username="alice", password="pass12345")
        self.bob = User.objects.create_user(username="bob", password="pass12345")

        self.alice_task = Task.objects.create(title="Задача Алисы", author=self.alice)
        self.bob_task = Task.objects.create(title="Задача Боба", author=self.bob)

        self.url = "/api/tasks/"

    def test_user_sees_only_own_tasks(self):
        self.client.force_authenticate(user=self.alice)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [t["title"] for t in response.data["results"]]
        self.assertIn("Задача Алисы", titles)
        self.assertNotIn("Задача Боба", titles)

    def test_user_cannot_retrieve_foreign_task(self):
        self.client.force_authenticate(user=self.alice)
        response = self.client.get(f"{self.url}{self.bob_task.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_update_foreign_task(self):
        self.client.force_authenticate(user=self.alice)
        response = self.client.patch(f"{self.url}{self.bob_task.id}/", {"title": "Взлом"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TaskCRUDTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pass12345")
        self.client.force_authenticate(user=self.user)
        self.url = "/api/tasks/"

    def test_create_task_sets_author_automatically(self):
        response = self.client.post(self.url, {"title": "Новая задача"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(id=response.data["id"])
        self.assertEqual(task.author, self.user)

    def test_create_task_ignores_author_from_payload(self):
        other = User.objects.create_user(username="bob", password="pass12345")
        response = self.client.post(self.url, {"title": "Задача", "author": other.id})
        task = Task.objects.get(id=response.data["id"])
        self.assertEqual(task.author, self.user)  # author из payload проигнорирован

    def test_list_tasks(self):
        Task.objects.create(title="Задача 1", author=self.user)
        Task.objects.create(title="Задача 2", author=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_retrieve_task(self):
        task = Task.objects.create(title="Задача", author=self.user)
        response = self.client.get(f"{self.url}{task.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Задача")

    def test_update_task_put(self):
        task = Task.objects.create(title="Старое", status="todo", author=self.user)
        response = self.client.put(
            f"{self.url}{task.id}/",
            {"title": "Новое", "status": "done", "description": ""},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.title, "Новое")
        self.assertEqual(task.status, "done")

    def test_partial_update_task_patch(self):
        task = Task.objects.create(title="Задача", status="todo", author=self.user)
        response = self.client.patch(f"{self.url}{task.id}/", {"status": "in_progress"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.status, "in_progress")

    def test_delete_task(self):
        task = Task.objects.create(title="Задача", author=self.user)
        response = self.client.delete(f"{self.url}{task.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=task.id).exists())


class TaskFilterSearchOrderingTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pass12345")
        self.client.force_authenticate(user=self.user)
        self.url = "/api/tasks/"

        Task.objects.create(title="Купить молоко", status="todo", author=self.user)
        Task.objects.create(title="Сделать отчёт", status="done", author=self.user)
        Task.objects.create(title="Помыть машину", status="in_progress", author=self.user)

    def test_filter_by_status(self):
        response = self.client.get(self.url, {"status": "done"})
        titles = [t["title"] for t in response.data["results"]]
        self.assertEqual(titles, ["Сделать отчёт"])

    def test_search_by_title(self):
        response = self.client.get(self.url, {"search": "молоко"})
        titles = [t["title"] for t in response.data["results"]]
        self.assertEqual(titles, ["Купить молоко"])

    def test_ordering_by_status(self):
        response = self.client.get(self.url, {"ordering": "status"})
        statuses = [t["status"] for t in response.data["results"]]
        self.assertEqual(statuses, sorted(statuses))


class JWTAuthFlowTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pass12345")

    def test_obtain_token_with_valid_credentials(self):
        response = self.client.post(
            "/api/auth/token/",
            {"username": "alice", "password": "pass12345"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_obtain_token_with_invalid_credentials(self):
        response = self.client.post(
            "/api/auth/token/",
            {"username": "alice", "password": "wrong"},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_protected_endpoint_with_token(self):
        token_response = self.client.post(
            "/api/auth/token/",
            {"username": "alice", "password": "pass12345"},
        )
        access = token_response.data["access"]
        response = self.client.get(
            "/api/tasks/", HTTP_AUTHORIZATION=f"Bearer {access}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_refresh_token(self):
        token_response = self.client.post(
            "/api/auth/token/",
            {"username": "alice", "password": "pass12345"},
        )
        refresh = token_response.data["refresh"]
        response = self.client.post("/api/auth/token/refresh/", {"refresh": refresh})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_logout_blacklists_refresh_token(self):
        token_response = self.client.post(
            "/api/auth/token/",
            {"username": "alice", "password": "pass12345"},
        )
        access = token_response.data["access"]
        refresh = token_response.data["refresh"]

        logout_response = self.client.post(
            "/api/auth/logout/token/",
            {"refresh": refresh},
            HTTP_AUTHORIZATION=f"Bearer {access}",
        )
        self.assertEqual(logout_response.status_code, status.HTTP_205_RESET_CONTENT)

        refresh_response = self.client.post("/api/auth/token/refresh/", {"refresh": refresh})
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)

class RegisterAPITests(APITestCase):
    def setUp(self):
        self.url = "/api/auth/register/"

    def test_register_creates_user_and_returns_tokens(self):
        response = self.client.post(
            self.url,
            {"username": "newuser", "password": "StrongPass123!", "email": "new@test.com"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_rejects_duplicate_username(self):
        User.objects.create_user(username="existing", password="pass12345")
        response = self.client.post(
            self.url,
            {"username": "existing", "password": "StrongPass123!"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_rejects_weak_password(self):
        response = self.client.post(
            self.url,
            {"username": "someone", "password": "123"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_endpoint_accessible_without_auth(self):
        # AllowAny — доступ должен быть даже без токена
        response = self.client.post(
            self.url,
            {"username": "anon", "password": "StrongPass123!"},
        )
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class UserListAPITests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username="admin", password="pass12345", email="admin@test.com")
        self.regular = User.objects.create_user(username="alice", password="pass12345")
        Task.objects.create(title="Задача 1", author=self.regular)
        Task.objects.create(title="Задача 2", author=self.regular)
        self.url = "/api/users/"

    def test_regular_user_cannot_access_user_list(self):
        self.client.force_authenticate(user=self.regular)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_cannot_access_user_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_can_access_user_list(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_task_count_is_correct(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)
        alice_data = next(u for u in response.data["results"] if u["username"] == "alice")
        self.assertEqual(alice_data["task_count"], 2)

class ProfileAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="OldPass123!", email="alice@test.com")
        self.client.force_authenticate(user=self.user)
        self.url = "/api/auth/me/"

    def test_get_own_profile(self):
        Task.objects.create(title="Задача", author=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "alice")
        self.assertEqual(response.data["task_count"], 1)

    def test_anonymous_cannot_access_profile(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_own_email(self):
        response = self.client.patch(self.url, {"email": "newemail@test.com"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "newemail@test.com")

    def test_cannot_update_username_via_profile(self):
        response = self.client.patch(self.url, {"username": "hacked"})
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "alice")  # username защищён read_only_fields


class ChangePasswordAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="OldPass123!")
        self.client.force_authenticate(user=self.user)
        self.url = "/api/auth/change-password/"

    def test_change_password_success(self):
        response = self.client.post(
            self.url,
            {"old_password": "OldPass123!", "new_password": "NewStrongPass456!"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewStrongPass456!"))

    def test_change_password_wrong_old_password(self):
        response = self.client.post(
            self.url,
            {"old_password": "WrongPass!", "new_password": "NewStrongPass456!"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_weak_new_password(self):
        response = self.client.post(
            self.url,
            {"old_password": "OldPass123!", "new_password": "123"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class TaskAdminAccessTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin", password="AdminPass123!", email="admin@test.com"
        )
        self.regular_user = User.objects.create_user(
            username="alice", password="pass12345"
        )
        self.changelist_url = reverse("admin:tasks_task_changelist")
        self.add_url = reverse("admin:tasks_task_add")

    def test_superuser_can_access_admin(self):
        self.client.login(username="admin", password="AdminPass123!")
        response = self.client.get(self.changelist_url)
        self.assertEqual(response.status_code, 200)

    def test_regular_user_redirected_from_admin(self):
        self.client.login(username="alice", password="pass12345")
        response = self.client.get(self.changelist_url)
        # Django admin редиректит не-staff на страницу логина (302)
        self.assertEqual(response.status_code, 302)

    def test_anonymous_redirected_from_admin(self):
        response = self.client.get(self.changelist_url)
        self.assertEqual(response.status_code, 302)


class TaskAdminFormTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin", password="AdminPass123!", email="admin@test.com"
        )
        self.client.login(username="admin", password="AdminPass123!")
        self.add_url = reverse("admin:tasks_task_add")

    def test_author_field_present_in_add_form(self):
        """Регрессионный тест: author должен быть в форме (баг из fieldsets)."""
        response = self.client.get(self.add_url)
        self.assertContains(response, 'name="author"')

    def test_can_create_task_via_admin(self):
        response = self.client.post(self.add_url, {
            "title": "Задача из админки",
            "description": "Тест",
            "status": "todo",
            "author": self.superuser.id,
        })
        # 302 = успешный редирект после сохранения
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(title="Задача из админки").exists())


class TaskAdminListViewTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin", password="AdminPass123!", email="admin@test.com"
        )
        self.client.login(username="admin", password="AdminPass123!")
        self.changelist_url = reverse("admin:tasks_task_changelist")

        Task.objects.create(title="Купить молоко", status="todo", author=self.superuser)
        Task.objects.create(title="Сделать отчёт", status="done", author=self.superuser)

    def test_changelist_shows_tasks(self):
        response = self.client.get(self.changelist_url)
        self.assertContains(response, "Купить молоко")
        self.assertContains(response, "Сделать отчёт")

    def test_search_by_title(self):
        response = self.client.get(self.changelist_url, {"q": "молоко"})
        self.assertContains(response, "Купить молоко")
        self.assertNotContains(response, "Сделать отчёт")

    def test_filter_by_status(self):
        response = self.client.get(self.changelist_url, {"status__exact": "done"})
        self.assertContains(response, "Сделать отчёт")
        self.assertNotContains(response, "Купить молоко")

class TaskAssignmentPermissionTests(APITestCase):
    def setUp(self):
        self.branch_head = User.objects.create_user(username="branch_head", password="pass12345")
        self.dept_head_a = User.objects.create_user(username="dept_head_a", password="pass12345")
        self.dept_head_b = User.objects.create_user(username="dept_head_b", password="pass12345")
        self.employee = User.objects.create_user(username="employee", password="pass12345")
        self.other_branch_head = User.objects.create_user(username="other_branch_head", password="pass12345")

        self.branch = Branch.objects.create(name="Москва", head=self.branch_head)
        self.other_branch = Branch.objects.create(name="Казань", head=self.other_branch_head)

        self.dept_a = Department.objects.create(name="Продажи", branch=self.branch, head=self.dept_head_a)
        self.dept_b = Department.objects.create(name="Поддержка", branch=self.branch, head=self.dept_head_b)
        self.other_dept = Department.objects.create(name="Логистика", branch=self.other_branch)

        # Profile.objects.create(user=self.dept_head_a, department=self.dept_a)
        Profile.objects.create(user=self.employee, department=self.dept_a)

        self.url = "/api/tasks/"

    def test_employee_can_create_personal_task(self):
        self.client.force_authenticate(user=self.employee)
        response = self.client.post(self.url, {"title": "Личная задача"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_employee_cannot_assign_task_to_department(self):
        self.client.force_authenticate(user=self.employee)
        response = self.client.post(self.url, {"title": "Задача", "department": self.dept_a.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_employee_cannot_assign_task_to_branch(self):
        self.client.force_authenticate(user=self.employee)
        response = self.client.post(self.url, {"title": "Задача", "branch": self.branch.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_department_head_can_assign_to_own_department(self):
        self.client.force_authenticate(user=self.dept_head_a)
        response = self.client.post(self.url, {"title": "Задача отделу", "department": self.dept_a.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_department_head_cannot_assign_to_foreign_department(self):
        self.client.force_authenticate(user=self.dept_head_a)
        response = self.client.post(self.url, {"title": "Задача", "department": self.dept_b.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_department_head_cannot_assign_to_branch(self):
        self.client.force_authenticate(user=self.dept_head_a)
        response = self.client.post(self.url, {"title": "Задача", "branch": self.branch.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_department_head_can_assign_to_own_employee(self):
        self.client.force_authenticate(user=self.dept_head_a)
        response = self.client.post(
            self.url, {"title": "Задача сотруднику", "assignee": self.employee.id}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_branch_head_can_assign_to_own_branch(self):
        self.client.force_authenticate(user=self.branch_head)
        response = self.client.post(self.url, {"title": "Задача филиалу", "branch": self.branch.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_branch_head_can_assign_to_department_in_own_branch(self):
        self.client.force_authenticate(user=self.branch_head)
        response = self.client.post(self.url, {"title": "Задача отделу", "department": self.dept_a.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_branch_head_cannot_assign_to_foreign_branch(self):
        self.client.force_authenticate(user=self.branch_head)
        response = self.client.post(self.url, {"title": "Задача", "branch": self.other_branch.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_branch_head_cannot_assign_to_department_in_foreign_branch(self):
        self.client.force_authenticate(user=self.branch_head)
        response = self.client.post(self.url, {"title": "Задача", "department": self.other_dept.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_branch_head_can_assign_to_department_head_personally(self):
        self.client.force_authenticate(user=self.branch_head)
        response = self.client.post(
            self.url, {"title": "Задача лично начальнику отдела", "assignee": self.dept_head_a.id}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TaskVisibilityTests(APITestCase):
    def setUp(self):
        self.branch_head = User.objects.create_user(username="branch_head", password="pass12345")
        self.dept_head = User.objects.create_user(username="dept_head", password="pass12345")
        self.other_dept_head = User.objects.create_user(username="other_dept_head", password="pass12345")
        self.employee_a = User.objects.create_user(username="employee_a", password="pass12345")
        self.employee_b = User.objects.create_user(username="employee_b", password="pass12345")

        self.branch = Branch.objects.create(name="Москва", head=self.branch_head)
        self.dept = Department.objects.create(name="Продажи", branch=self.branch, head=self.dept_head)
        self.other_dept = Department.objects.create(name="Поддержка", branch=self.branch, head=self.other_dept_head)

        # Profile.objects.create(user=self.dept_head, department=self.dept)
        Profile.objects.create(user=self.employee_a, department=self.dept)
        Profile.objects.create(user=self.employee_b, department=self.other_dept)

        self.url = "/api/tasks/"

    def test_department_wide_task_visible_to_all_department_employees(self):
        Task.objects.create(title="Задача отделу", author=self.dept_head, department=self.dept)

        self.client.force_authenticate(user=self.employee_a)
        response = self.client.get(self.url)
        titles = [t["title"] for t in response.data["results"]]
        self.assertIn("Задача отделу", titles)

    def test_department_wide_task_not_visible_to_other_department(self):
        Task.objects.create(title="Задача отделу", author=self.dept_head, department=self.dept)

        self.client.force_authenticate(user=self.employee_b)
        response = self.client.get(self.url)
        titles = [t["title"] for t in response.data["results"]]
        self.assertNotIn("Задача отделу", titles)

    def test_branch_wide_task_visible_to_all_department_heads(self):
        Task.objects.create(title="Задача филиалу", author=self.branch_head, branch=self.branch)

        self.client.force_authenticate(user=self.dept_head)
        response = self.client.get(self.url)
        titles = [t["title"] for t in response.data["results"]]
        self.assertIn("Задача филиалу", titles)

        self.client.force_authenticate(user=self.other_dept_head)
        response = self.client.get(self.url)
        titles = [t["title"] for t in response.data["results"]]
        self.assertIn("Задача филиалу", titles)

    def test_branch_wide_task_not_visible_to_regular_employee(self):
        Task.objects.create(title="Задача филиалу", author=self.branch_head, branch=self.branch)

        self.client.force_authenticate(user=self.employee_a)
        response = self.client.get(self.url)
        titles = [t["title"] for t in response.data["results"]]
        self.assertNotIn("Задача филиалу", titles)

    def test_task_assigned_to_specific_person_visible_only_to_them(self):
        Task.objects.create(
            title="Личная задача от начальника",
            author=self.dept_head,
            department=self.dept,
            assignee=self.employee_a,
        )

        self.client.force_authenticate(user=self.employee_a)
        response = self.client.get(self.url)
        titles = [t["title"] for t in response.data["results"]]
        self.assertIn("Личная задача от начальника", titles)

    def test_department_head_still_sees_task_after_assignment(self):
        """Начальник отдела сохраняет видимость задачи даже после назначения конкретному сотруднику."""
        Task.objects.create(
            title="Делегированная задача",
            author=self.dept_head,
            department=self.dept,
            assignee=self.employee_a,
        )

        self.client.force_authenticate(user=self.dept_head)
        response = self.client.get(self.url)
        titles = [t["title"] for t in response.data["results"]]
        self.assertIn("Делегированная задача", titles)

    def test_regular_employee_does_not_see_personal_task_of_colleague(self):
        Task.objects.create(title="Личная задача коллеги", author=self.employee_a)

        self.client.force_authenticate(user=self.employee_b)
        response = self.client.get(self.url)
        titles = [t["title"] for t in response.data["results"]]
        self.assertNotIn("Личная задача коллеги", titles)