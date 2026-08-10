from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Task(models.Model):
    """Модель для задач"""

    STATUS_CHOICES = [
        ('todo', 'К выполнению'),
        ('in_progress', 'в процессе'),
        ('done', 'Выполнено')
    ]

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='Автор'
    )
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        verbose_name='Исполнитель'
    )
    branch = models.ForeignKey(
        'organizations.Branch',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='branch_tasks',
        verbose_name='Филиал (адресат)'
    )
    department = models.ForeignKey(
        'organizations.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='department_tasks',
        verbose_name='Отдел (адресат)'
    )
    title = models.CharField(
        max_length= 200,
        verbose_name = 'Название Задачи'
    )
    description = models.TextField(
        blank = True,
        verbose_name='Описание'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='todo',
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Обновлено'
    )
    due_date = models.DateTimeField(
        null= True,
        blank=True,
        verbose_name='Срок выполнения'
    )
    class Meta:
        verbose_name='Задача'
        verbose_name_plural = 'Задачи'
        ordering=['-created_at']

    def __str__(self):
        return self.title