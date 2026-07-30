# Django Todo Backend

Backend для Todo-листа на Django + Django REST Framework (DRF).
Проект сделан как учебный: сначала API, потом отдельный frontend.

## Содержание
- [Что это](#что-это)
- [Что уже сделано](#что-уже-сделано)
- [Технологии](#технологии)
- [Быстрый старт](#быстрый-старт)
- [Основные URL](#основные-url)
- [API эндпоинты](#api-эндпоинты)
- [Примеры запросов](#примеры-запросов)
- [Тестирование](#тестирование)
- [Разработка](#разработка)
- [Roadmap](#roadmap)
- [Контакты](#контакты)

## Что это
Простой сервис для управления задачами: создать задачу, менять статус, редактировать описание, удалять, фильтровать и искать. Каждый пользователь видит и управляет только своими задачами.

## Что уже сделано
- [x] Модель Task (title, description, status, created_at, updated_at, due_date, author).
- [x] Django Admin Panel для управления задачами и пользователями.
- [x] REST API на DRF:
  - [x] CRUD (list/create/retrieve/update/partial_update/destroy).
  - [x] Пагинация.
  - [x] Фильтрация (django-filter).
  - [x] Сортировка (ordering).
  - [x] Поиск (search).
- [x] JWT аутентификация (djangorestframework-simplejwt).
- [x] Сессионная авторизация (для Browsable API).
- [x] Регистрация новых пользователей (POST /api/auth/register/), сразу с выдачей JWT-токенов.
- [x] Logout с отзывом refresh-токена (token blacklist).
- [x] Ограничение доступа: только аутентифицированные пользователи.
- [x] Задачи привязаны к пользователю (author), изоляция данных между пользователями.
- [x] Список пользователей с количеством задач — только для admin/staff (GET /api/users/).
- [x] SECRET_KEY и DEBUG вынесены в переменные окружения (.env).
- [x] Тесты API (unit/integration) — модели, permissions, изоляция данных, CRUD, фильтры, JWT-флоу, регистрация, список пользователей.
- [ ] PostgreSQL вместо SQLite (планируется).
- [x] Документация API (OpenAPI/Swagger) (планируется).
- [ ] Deployment (планируется).

## Технологии
- Python 3.11+
- Django 6.0
- Django REST Framework
- django-filter
- djangorestframework-simplejwt
- python-dotenv

## Быстрый старт
### 1) Клонировать репозиторий

    git clone https://github.com/K1R1UUS/django-todo-backend.git
    cd django-todo-backend

### 2) Создать и активировать venv

#### Windows:

    python -m venv venv
    venv\Scripts\activate

#### macOS/Linux:

    python -m venv venv
    source venv/bin/activate

### 3) Установить зависимости

    pip install -r requirements.txt

### 4) Настроить переменные окружения

Создать файл `.env` в корне проекта (рядом с `manage.py`):

    SECRET_KEY=твой-секретный-ключ
    DEBUG=True

Сгенерировать ключ можно командой:

    python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

### 5) Применить миграции

    python manage.py migrate

### 6) Создать суперпользователя

    python manage.py createsuperuser

### 7) Запустить сервер

    python manage.py runserver

## Основные URL

    Admin: http://127.0.0.1:8000/admin/

    API root (Browsable API): http://127.0.0.1:8000/api/

    Tasks: http://127.0.0.1:8000/api/tasks/

    Users (только admin/staff): http://127.0.0.1:8000/api/users/

    Auth: http://127.0.0.1:8000/api/auth/

    Важно: UI на /api/ — это DRF Browsable API (удобный интерфейс для тестирования API), не "пользовательский фронтенд".

## API эндпоинты

### Authentication

    POST /api/auth/register/ — регистрация нового пользователя (возвращает JWT-токены сразу).
    POST /api/auth/token/ — получить токены (access + refresh).
    POST /api/auth/token/refresh/ — обновить access токен.
    POST /api/auth/logout/token/ — отозвать (blacklist) refresh-токен, для JWT-клиентов.
    GET /api/auth/logout/ — выход из сессии (редирект на /login/), для Browsable API.
    GET /api/auth/me/ — посмотреть свой профиль (username, email, date_joined, task_count).
    PATCH /api/auth/me/ — обновить email в своём профиле.
    POST /api/auth/change-password/ — сменить пароль (требует старый пароль).

### Tasks (требует аутентификации)

    GET /api/tasks/ — список задач пользователя (с пагинацией).

    POST /api/tasks/ — создать задачу.

    GET /api/tasks/{id}/ — получить задачу.

    PUT /api/tasks/{id}/ — заменить задачу целиком.

    PATCH /api/tasks/{id}/ — частично обновить задачу.

    DELETE /api/tasks/{id}/ — удалить задачу.

### Users (требует прав admin/staff)

    GET /api/users/ — список пользователей с количеством задач (task_count).

    GET /api/users/{id}/ — детали конкретного пользователя.

### Query-параметры (Tasks)

    Пагинация:

        GET /api/tasks/?page=2

    Фильтрация:

        GET /api/tasks/?status=done

    Сортировка:

        GET /api/tasks/?ordering=due_date

        GET /api/tasks/?ordering=-created_at

    Поиск:

        GET /api/tasks/?search=молоко

## Примеры запросов

#### Регистрация

    curl -X POST http://127.0.0.1:8000/api/auth/register/ \
      -H "Content-Type: application/json" \
      -d "{\"username\":\"newbie\",\"password\":\"StrongPass123!\",\"email\":\"newbie@test.com\"}"

#### Получить токены (login)

    curl -X POST http://127.0.0.1:8000/api/auth/token/ \
      -H "Content-Type: application/json" \
      -d "{\"username\":\"your_username\",\"password\":\"your_password\"}"

#### Создать задачу (POST)

    curl -X POST http://127.0.0.1:8000/api/tasks/ \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
      -d "{\"title\":\"Купить молоко\",\"description\":\"2 литра\",\"status\":\"todo\"}"

#### Список задач (GET)

    curl http://127.0.0.1:8000/api/tasks/ \
      -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

#### Обновить токен

    curl -X POST http://127.0.0.1:8000/api/auth/token/refresh/ \
      -H "Content-Type: application/json" \
      -d "{\"refresh\":\"YOUR_REFRESH_TOKEN\"}"

#### Выход (JWT — отзыв refresh-токена)

    curl -X POST http://127.0.0.1:8000/api/auth/logout/token/ \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
      -d "{\"refresh\":\"YOUR_REFRESH_TOKEN\"}"

#### Список пользователей (только admin/staff)

    curl http://127.0.0.1:8000/api/users/ \
      -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"

#### Посмотреть свой профиль

    curl http://127.0.0.1:8000/api/auth/me/ \
      -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

#### Обновить email в профиле

    curl -X PATCH http://127.0.0.1:8000/api/auth/me/ \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
      -d "{\"email\":\"newemail@test.com\"}"

#### Сменить пароль

    curl -X POST http://127.0.0.1:8000/api/auth/change-password/ \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
      -d "{\"old_password\":\"OldPass123!\",\"new_password\":\"NewStrongPass456!\"}"

## Тестирование

Проект покрыт unit/integration тестами (`tasks/tests.py`):

- Модель Task (`__str__`, дефолтные значения, ordering).
- Permissions — анонимный пользователь не имеет доступа.
- Изоляция данных — пользователи не видят чужие задачи.
- CRUD операции над задачами.
- Фильтрация, поиск, сортировка.
- JWT-флоу: получение токена, доступ по токену, refresh, logout с blacklist.
- Регистрация: успешная, дубль username, слабый пароль, доступ без авторизации.
- Список пользователей: доступ только для admin/staff, корректный подсчёт task_count.

Запуск тестов:

    python manage.py test tasks

## Документация API (Swagger/OpenAPI)

    Swagger UI: http://127.0.0.1:8000/api/docs/
    ReDoc: http://127.0.0.1:8000/api/redoc/
    OpenAPI схема (JSON): http://127.0.0.1:8000/api/schema/


## Разработка
### Полезные команды

- Создать миграции:

      python manage.py makemigrations

- Применить миграции:

      python manage.py migrate

- Проверить проект:

      python manage.py check

- Запустить тесты:

      python manage.py test tasks

## Roadmap

План (вдохновлён учебным роадмапом):

  - [x] JWT токены (djangorestframework-simplejwt), логин/refresh/logout с blacklist.
  - [x] Permissions: защита эндпоинтов.
  - [x] Привязка задач к пользователю (author), изоляция данных.
  - [x] Регистрация пользователей.
  - [x] Список пользователей для admin/staff.
  - [x] SECRET_KEY и DEBUG через переменные окружения.
  - [x] Тесты API (unit/integration).
  - [ ] PostgreSQL (переезд с SQLite).
  - [x] Документация API (Swagger/OpenAPI).
  - [ ] Deployment (Render/Railway), CORS.
  - [x] Смена пароля / профиль пользователя (GET /api/auth/me/).
  - [ ] Отдельный frontend (React/Vue/Next) и интеграция с этим API.

## Контакты

    GitHub: @K1R1UUS

    Email: kk.pichuginn@gmail.com

Обновлено: 29 июля 2026