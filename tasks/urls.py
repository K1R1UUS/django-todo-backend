from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, UserListViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"users", UserListViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
]