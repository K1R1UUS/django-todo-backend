from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Task
from .serializers import TaskSerializer

class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    
    filterset_fields = ["status"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "due_date", "status"]
    ordering = ["-created_at"]

