from django.db.models import Q
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import Task
from .serializers import TaskSerializer, UserListSerializer
from .permissions import CanAssignTaskTarget, get_visible_tasks

class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, CanAssignTaskTarget]

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]

    filterset_fields = ["status"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "due_date", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return get_visible_tasks(self.request.user)

        user_department = getattr(getattr(user, "profile", None), "department", None)
        if user_department:
            visibility |= Q(department=user_department, assignee__isnull=True)

        if hasattr(user, "headed_department"):
            own_branch = user.headed_department.branch
            visibility |= Q(branch=own_branch, department__isnull=True)

        return self.queryset.filter(visibility).distinct()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class UserListViewSet(ReadOnlyModelViewSet):
    """Список пользователей — только для staff/admin."""
    from django.db.models import Count
    queryset = User.objects.annotate(task_count=Count("tasks")).order_by("-date_joined")
    serializer_class = UserListSerializer
    permission_classes = [IsAdminUser]