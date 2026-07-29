from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from django.db.models import Count

from .models import Task
from .serializers import TaskSerializer, UserListSerializer


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]

    filterset_fields = ["status"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "due_date", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        if self.request.user and self.request.user.is_authenticated:
            return self.queryset.filter(author=self.request.user)
        return Task.objects.none()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class UserListViewSet(ReadOnlyModelViewSet):
    """Список пользователей — только для staff/admin."""
    queryset = User.objects.annotate(task_count=Count("tasks")).order_by("-date_joined")
    serializer_class = UserListSerializer
    permission_classes = [IsAdminUser]