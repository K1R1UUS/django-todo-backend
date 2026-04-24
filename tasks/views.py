from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Task
from .serializers import TaskSerializer

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

