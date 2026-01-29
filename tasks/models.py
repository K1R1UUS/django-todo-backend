from django.db import models
from django.utils import timezone

class Task(models.Model):
    """Модель для задач"""

    STATUS_CHOICES = [
        ('todo', 'К выполнению'),
        ('in_progress', 'в процессе'),
        ('done', 'Выполнено')
    ]

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