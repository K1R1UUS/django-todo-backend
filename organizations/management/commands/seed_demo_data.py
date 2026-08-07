import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from organizations.models import Branch, Department, Profile
from tasks.models import Task


TASK_TITLES = [
    "Подготовить квартальный отчёт",
    "Обновить документацию по процессу",
    "Провести встречу с клиентом",
    "Проверить показатели за месяц",
    "Согласовать бюджет на след. квартал",
    "Обучить нового сотрудника",
    "Настроить оборудование в офисе",
    "Подготовить презентацию для руководства",
]


class Command(BaseCommand):
    help = "Создаёт демо-данные: филиалы, отделы, сотрудников, задачи."

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            type=str,
            default="DemoPass123!",
            help="Пароль для всех демо-пользователей (по умолчанию DemoPass123!)",
        )

    def handle(self, *args, **options):
        password = options["password"]

        self.stdout.write("Создаю пользователей...")
        users = self._create_users(password)

        self.stdout.write("Создаю филиалы и отделы...")
        branches = self._create_branches_and_departments(users)

        self.stdout.write("Привязываю сотрудников к отделам...")
        self._assign_employees(users, branches)

        self.stdout.write("Создаю задачи...")
        self._create_tasks(users)

        self.stdout.write(self.style.SUCCESS(
            f"\nГотово! Создано {len(users)} пользователей, пароль для всех: {password}"
        ))
        self.stdout.write(self.style.SUCCESS(
            "Логины: " + ", ".join(u.username for u in users)
        ))

    def _create_users(self, password):
        usernames = [
            "ivanov", "petrov", "sidorova", "kuznetsov",
            "smirnova", "popov", "vasilieva", "fedorov",
        ]
        users = []
        for username in usernames:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": f"{username}@demo.local"},
            )
            if created:
                user.set_password(password)
                user.save()
            users.append(user)
        return users

    def _create_branches_and_departments(self, users):
        branch_moscow = Branch.objects.create(
            name="Москва",
            address="ул. Тверская, 1",
            head=users[0],  # ivanov — начальник филиала
        )
        branch_kazan = Branch.objects.create(
            name="Казань",
            address="ул. Баумана, 10",
            head=users[1],  # petrov — начальник филиала
        )

        Department.objects.create(name="Продажи", branch=branch_moscow, head=users[2])   # sidorova
        Department.objects.create(name="Поддержка", branch=branch_moscow, head=users[3]) # kuznetsov
        Department.objects.create(name="Логистика", branch=branch_kazan, head=users[4])  # smirnova
        Department.objects.create(name="Маркетинг", branch=branch_kazan, head=users[5])  # popov

        return {"moscow": branch_moscow, "kazan": branch_kazan}

    def _assign_employees(self, users, branches):
        departments = list(Department.objects.all())

        # Начальники тоже привязаны к своим отделам как сотрудники
        head_department_map = {d.head_id: d for d in departments if d.head_id}
        for user in users:
            department = head_department_map.get(user.id)
            if department is None:
                # оставшихся сотрудников раскидываем по отделам случайно
                department = random.choice(departments)
            Profile.objects.get_or_create(user=user, defaults={"department": department})

    def _create_tasks(self, users):
        statuses = ["todo", "in_progress", "done"]
        for _ in range(20):
            author = random.choice(users)
            Task.objects.create(
                title=random.choice(TASK_TITLES),
                description="Демо-задача для тестирования.",
                status=random.choice(statuses),
                author=author,
                due_date=timezone.now() + timedelta(days=random.randint(-5, 20)),
            )