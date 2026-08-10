# Django Todo Backend

Backend для корпоративного таск-трекера на Django + Django REST Framework (DRF).
Проект сделан как учебный: сначала API, потом отдельный frontend.

## Содержание
- [Что это](#что-это)
- [Что уже сделано](#что-уже-сделано)
- [Технологии](#технологии)
- [Быстрый старт](#быстрый-старт)
- [Основные URL](#основные-url)
- [Модель данных](#модель-данных)
- [API эндпоинты](#api-эндпоинты)
- [Логика делегирования задач](#логика-делегирования-задач)
- [Примеры запросов](#примеры-запросов)
- [Тестирование](#тестирование)
- [Разработка](#разработка)
- [Roadmap](#roadmap)
- [Контакты](#контакты)

## Что это
Сервис для управления задачами внутри компании со структурой филиалов и отделов. Поддерживает как личные задачи (todo-лист для себя), так и делегирование: начальник филиала может поставить задачу всему филиалу, конкретному отделу или лично начальнику отдела; начальник отдела — своему отделу или конкретному сотруднику.

## Что уже сделано

**Основы**
- [x] REST API на DRF: CRUD, пагинация, фильтрация (django-filter), сортировка, поиск.
- [x] JWT аутентификация (djangorestframework-simplejwt) + сессионная авторизация для Browsable API.
- [x] Регистрация пользователей (POST /api/auth/register/) с выдачей JWT сразу.
- [x] Logout с отзывом refresh-токена (token blacklist).
- [x] Профиль пользователя (GET/PATCH /api/auth/me/) и смена пароля.
- [x] Список пользователей с количеством задач — только для admin/staff.
- [x] SECRET_KEY и DEBUG вынесены в переменные окружения (.env).
- [x] Документация API (Swagger UI / ReDoc) через drf-spectacular.

**Организационная структура**
- [x] Модели Branch (филиал), Department (отдел), Profile (сотрудник: отдел + должность).
- [x] Роль сотрудника (начальник филиала / начальник отдела / рядовой) выводится из связей `head`, а не хранится отдельным полем.
- [x] Просмотр структуры филиала/отдела через API с правами по иерархии (admin → начальник филиала → начальник отдела).
- [x] Management-команда `seed_demo_data` для генерации демо-данных.

**Задачи и делегирование**
- [x] Задача может быть личной, адресованной отделу, филиалу или конкретному сотруднику (author/assignee/department/branch).
- [x] Иерархическая видимость задач в зависимости от роли (см. раздел ниже).
- [x] Права на назначение задач проверяются по оргструктуре (нельзя адресовать чужой отдел/филиал).

**Тесты**
- [x] 80+ unit/integration тестов: модели, permissions, изоляция данных, CRUD, JWT-флоу, регистрация, оргструктура, делегирование задач, admin-панель.

**В планах**
- [ ] PostgreSQL вместо SQLite.
- [ ] Deployment (Render/Railway), CORS.
- [ ] Простой веб-фронтенд для пилотного использования.

## Технологии
- Python 3.11+
- Django 6.0
- Django REST Framework
- django-filter
- djangorestframework-simplejwt
- drf-spectacular
- python-dotenv

## Быстрый старт

### 1) Клонировать репозиторий

    git clone https://github.com/K1R1UUS/django-todo-backend.git
    cd django-todo-backend

### 2) Создать и активировать venv

Windows:

    python -m venv venv
    venv\Scripts\activate

macOS/Linux:

    python -m venv venv
    source venv/bin/activate

### 3) Установить зависимости

    pip install -r requirements.txt

### 4) Настроить переменные окружения

Создать файл `.env` в корне проекта (рядом с `manage.py`):

    SECRET_KEY=твой-секретный-ключ
    DEBUG=True

Сгенерировать ключ:

    python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

### 5) Применить миграции

    python manage.py migrate

### 6) Создать суперпользователя

    python manage.py createsuperuser

### 7) (опционально) Засеять демо-данные

    python manage.py seed_demo_data

Создаст 2 филиала, 4 отдела, 8 сотрудников (пароль по умолчанию `DemoPass123!`) и 20 случайных задач.

### 8) Запустить сервер

    python manage.py runserver

## Основные URL

    Admin: http://127.0.0.1:8000/admin/
    API root (Browsable API): http://127.0.0.1:8000/api/
    Tasks: http://127.0.0.1:8000/api/tasks/
    Branches: http://127.0.0.1:8000/api/branches/
    Users (только admin/staff): http://127.0.0.1:8000/api/users/
    Auth: http://127.0.0.1:8000/api/auth/
    Swagger UI: http://127.0.0.1:8000/api/docs/
    ReDoc: http://127.0.0.1:8000/api/redoc/

## Модель данных

**Branch (Филиал)** — name, head (начальник филиала, User).

**Department (Отдел)** — name, branch (FK), head (начальник отдела, User). Уникальность имени в рамках филиала.

**Profile (Профиль сотрудника)** — user (OneToOne), department (FK, опционально), position (должность, например "Инженер 3-й категории").

**Task (Задача)** — title, description, status, due_date, author (создатель), а также поля адресации:
- `assignee` — если задача назначена конкретному человеку;
- `department` — если задача адресована всему отделу;
- `branch` — если задача адресована всему филиалу.

Роль пользователя (начальник филиала/отдела) не хранится отдельно — вычисляется через `Branch.head`/`Department.head`.

## API эндпоинты

### Authentication

    POST /api/auth/register/ — регистрация (возвращает JWT-токены сразу).
    POST /api/auth/token/ — получить токены (access + refresh).
    POST /api/auth/token/refresh/ — обновить access токен.
    POST /api/auth/logout/token/ — отозвать (blacklist) refresh-токен.
    GET  /api/auth/logout/ — выход из сессии (для Browsable API).
    GET  /api/auth/me/ — свой профиль (username, email, date_joined, task_count).
    PATCH /api/auth/me/ — обновить email.
    POST /api/auth/change-password/ — сменить пароль.

### Tasks (требует аутентификации)

    GET    /api/tasks/ — список видимых пользователю задач (с пагинацией).
    POST   /api/tasks/ — создать задачу (author, опционально assignee/department/branch).
    GET    /api/tasks/{id}/ — получить задачу.
    PUT    /api/tasks/{id}/ — заменить задачу целиком.
    PATCH  /api/tasks/{id}/ — частично обновить (например, переадресовать).
    DELETE /api/tasks/{id}/ — удалить задачу.

Query-параметры: `?page=2`, `?status=done`, `?ordering=-created_at`, `?search=молоко`.

### Organizations (структура компании)

    GET /api/branches/ — список всех филиалов со структурой (только admin/staff).
    GET /api/branches/{id}/structure/ — отделы, начальники, сотрудники филиала (admin или начальник этого филиала).
    GET /api/departments/{id}/structure/ — начальник и сотрудники отдела (admin, начальник отдела, или начальник филиала-владельца).

### Users (только admin/staff)

    GET /api/users/ — список пользователей с количеством задач.
    GET /api/users/{id}/ — детали пользователя.

## Логика делегирования задач

**Кто что может адресовать при создании задачи:**

| Роль | Может назначить |
|---|---|
| Рядовой сотрудник | Только личную задачу (без department/branch) |
| Начальник отдела | Свой отдел целиком, или конкретного сотрудника своего отдела |
| Начальник филиала | Весь филиал, любой отдел филиала, или лично начальника отдела |
| Admin/staff | Что угодно |

**Кто видит задачу:**

- Автор — всегда видит то, что создал.
- Исполнитель (`assignee`) — видит задачи, назначенные лично ему.
- Все сотрудники отдела — если задача адресована отделу (`department` задан, `assignee` пуст).
- Все начальники отделов филиала — если задача адресована филиалу (`branch` задан, `department` пуст).
- При уточнении адресата (например, начальник отдела передаёт задачу конкретному сотруднику) поле `department` не сбрасывается — начальник отдела сохраняет видимость для контроля.

## Примеры запросов

#### Регистрация

    curl -X POST http://127.0.0.1:8000/api/auth/register/ \
      -H "Content-Type: application/json" \
      -d "{\"username\":\"newbie\",\"password\":\"StrongPass123!\",\"email\":\"newbie@test.com\"}"

#### Получить токены (login)

    curl -X POST http://127.0.0.1:8000/api/auth/token/ \
      -H "Content-Type: application/json" \
      -d "{\"username\":\"your_username\",\"password\":\"your_password\"}"

#### Создать личную задачу

    curl -X POST http://127.0.0.1:8000/api/tasks/ \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
      -d "{\"title\":\"Купить молоко\",\"description\":\"2 литра\",\"status\":\"todo\"}"

#### Начальник отдела ставит задачу всему отделу

    curl -X POST http://127.0.0.1:8000/api/tasks/ \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer DEPT_HEAD_TOKEN" \
      -d "{\"title\":\"Сдать отчёт до пятницы\",\"department\":1}"

#### Начальник филиала ставит задачу лично начальнику отдела

    curl -X POST http://127.0.0.1:8000/api/tasks/ \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer BRANCH_HEAD_TOKEN" \
      -d "{\"title\":\"Подготовить план на квартал\",\"assignee\":5}"

#### Список задач (GET)

    curl http://127.0.0.1:8000/api/tasks/ \
      -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

#### Структура филиала

    curl http://127.0.0.1:8000/api/branches/1/structure/ \
      -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

#### Выход (JWT — отзыв refresh-токена)

    curl -X POST http://127.0.0.1:8000/api/auth/logout/token/ \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
      -d "{\"refresh\":\"YOUR_REFRESH_TOKEN\"}"

## Тестирование

Проект покрыт 80+ unit/integration тестами:

- **tasks/tests.py**: модель Task, permissions, изоляция данных, CRUD, фильтры/поиск/сортировка, JWT-флоу, регистрация, профиль, смена пароля, список пользователей, admin-панель, права на адресацию задач, иерархическая видимость.
- **organizations/tests.py**: доступ к структуре филиала/отдела по ролям (admin/начальник филиала/начальник отдела/сотрудник).

Запуск всех тестов:

    python manage.py test

Запуск тестов конкретного приложения:

    python manage.py test tasks
    python manage.py test organizations

## Разработка
### Полезные команды

    python manage.py makemigrations   # создать миграции
    python manage.py migrate          # применить миграции
    python manage.py check            # проверить проект
    python manage.py test             # прогнать все тесты
    python manage.py seed_demo_data   # создать демо-данные

## Roadmap

  - [x] JWT токены, логин/refresh/logout с blacklist.
  - [x] Permissions: защита эндпоинтов.
  - [x] Регистрация, профиль, смена пароля.
  - [x] Список пользователей для admin/staff.
  - [x] SECRET_KEY и DEBUG через переменные окружения.
  - [x] Документация API (Swagger/OpenAPI).
  - [x] Организационная структура (филиалы, отделы, должности).
  - [x] Делегирование задач по иерархии с полным тестовым покрытием.
  - [ ] PostgreSQL (переезд с SQLite).
  - [ ] Deployment (Render/Railway), CORS.
  - [ ] Простой веб-фронтенд для пилотного использования.
  - [ ] Отдельный полноценный frontend (React/Vue/Next).

## Контакты

    GitHub: @K1R1UUS
    Email: kk.pichuginn@gmail.com

Обновлено: 6 августа 2026