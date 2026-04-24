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
- [Разработка](#разработка)
- [Roadmap](#roadmap)
- [Контакты](#контакты)

## Что это
Простой сервис для управления задачами: создать задачу, менять статус, редактировать описание, удалять, фильтровать и искать.

## Что уже сделано
- [x] Модель Task (title, description, status, created_at, updated_at, due_date, author).
- [x] Django Admin Panel для управления задачами.
- [x] REST API на DRF:
  - [x] CRUD (list/create/retrieve/update/partial_update/destroy).
  - [x] Пагинация.
  - [x] Фильтрация (django-filter).
  - [x] Сортировка (ordering).
  - [x] Поиск (search).
- [x] JWT аутентификация (djangorestframework-simplejwt).
- [x] Сессионная авторизация (для Browsable API).
- [x] Ограничение доступа: только аутентифицированные пользователи.
- [x] Задачи привязаны к пользователю (author).
- [ ] PostgreSQL вместо SQLite (планируется).
- [ ] Документация API (OpenAPI/Swagger) (планируется).
- [ ] Deployment (планируется).

## Технологии
- Python 3.11+
- Django 6.0
- Django REST Framework
- django-filter
- djangorestframework-simplejwt

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

### 4) Применить миграции

    python manage.py migrate

### 5) Создать суперпользователя

    python manage.py createsuperuser

### 6) Запустить сервер

    python manage.py runserver

## Основные URL

    Admin: http://127.0.0.1:8000/admin/

    API root (Browsable API): http://127.0.0.1:8000/api/

    Tasks: http://127.0.0.1:8000/api/tasks/

    Auth: http://127.0.0.1:8000/api/auth/

    Важно: UI на /api/ — это DRF Browsable API (удобный интерфейс для тестирования API), не "пользовательский фронтенд".

## API эндпоинты
### Authentication

    POST /api/auth/token/ — получить токены (access + refresh).
    POST /api/auth/token/refresh/ — обновить access токен.
    GET /api/auth/logout/ — выход из сессии (редирект на /login/).

### Authentication (JWT для API)

    POST /api/auth/token/ — получить токены JWT.

### Tasks (требует аутентификации)

    GET /api/tasks/ — список задач пользователя (с пагинацией).

    POST /api/tasks/ — создать задачу.

    GET /api/tasks/{id}/ — получить задачу.

    PUT /api/tasks/{id}/ — заменить задачу целиком.

    PATCH /api/tasks/{id}/ — частично обновить задачу.

    DELETE /api/tasks/{id}/ — удалить задачу.

### Query-параметры

    Пагинация:

        GET /api/tasks/?page=2

    Фильтрация:

        GET /api/tasks/?status=done

    Сортировка:

        GET /api/tasks/?ordering=due_date

        GET /api/tasks/?ordering=-created_at

    Поиск:

        GET /api/tasks/?search=молоко

### Примеры запросов
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

#### Выход (logout)

    curl -X POST http://127.0.0.1:8000/api/auth/logout/ \
      -H "Content-Type: application/json" \
      -d "{\"refresh\":\"YOUR_REFRESH_TOKEN\"}"

## Разработка
### Полезные команды

- [Создать миграции:]

    python manage.py makemigrations

- [Применить миграции:]

    python manage.py migrate

- [Проверить проект:]

    python manage.py check

## Roadmap

План (вдохновлён учебным роадмапом):

  - [x] JWT токены (djangorestframework-simplejwt), логин/refresh/ logout.
  - [x] Permissions: защита эндпоинтов.
  - [x] Привязка задач к пользователю (author).
  - [ ] PostgreSQL (переезд с SQLite).
  - [ ] Тесты API (unit/integration).
  - [ ] Документация API (Swagger/OpenAPI).
  - [ ] Deployment (Render/Railway), переменные окружения, HTTPS, CORS.
  - [ ] Отдельный frontend (React/Vue/Next) и интеграция с этим API.

## Контакты

    GitHub: @K1R1UUS

    Email: kk.pichuginn@gmail.com

Обновлено: 24 апреля 2026