#Django Todo Backend

Простое приложение на Django/DRF для управления задачами (Todo).​
##🚀 Особенности

    ✅ Django Admin Panel (/admin/).​

    ✅ REST API на DRF (/api/).​

    ✅ CRUD для задач: create/list/retrieve/update/delete.

    ✅ Фильтрация (django-filter), сортировка (ordering), поиск (search), пагинация.

##📋 Технологии

    Python 3.11+

    Django

    Django REST Framework

    django-filter​

##🔧 Установка и запуск
###1) Клонировать репозиторий

git clone https://github.com/K1R1UUS/django-todo-backend.git
cd django-todo-backend

###2) Виртуальное окружение

####Windows:

python -m venv venv
venv\Scripts\activate

####macOS/Linux:

python -m venv venv
source venv/bin/activate

###3) Установить зависимости

pip install -r requirements.txt

###4) Миграции

python manage.py migrate

###5) Суперпользователь (для админки)

python manage.py createsuperuser

###6) Запуск сервера

python manage.py runserver

##🌐 URLs

    Admin: http://127.0.0.1:8000/admin/​

    API root: http://127.0.0.1:8000/api/​

    Tasks: http://127.0.0.1:8000/api/tasks/​

##🔌 Примеры API запросов

    List (пагинация): GET /api/tasks/?page=2​

    Filter: GET /api/tasks/?status=done​

    Ordering: GET /api/tasks/?ordering=-created_at​

    Search: GET /api/tasks/?search=молоко​

##🎯 Следующие шаги

    JWT аутентификация (SimpleJWT) + permissions.​

    Unit-тесты API.

    Переход на PostgreSQL.

    Документация API (OpenAPI/Swagger) и деплой.