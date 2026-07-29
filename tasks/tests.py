from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Task


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