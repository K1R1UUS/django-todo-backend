from django.urls import path
from . import web_views

urlpatterns = [
    path("tasks/", web_views.task_list_view, name="web-task-list"),
    path("tasks/new/", web_views.task_create_view, name="web-task-create"),
    path("tasks/<int:pk>/edit/", web_views.task_edit_view, name="web-task-edit"),
    path("tasks/<int:pk>/delete/", web_views.task_delete_view, name="web-task-delete"),
    path("profile/", web_views.profile_view, name="web-profile"),
]