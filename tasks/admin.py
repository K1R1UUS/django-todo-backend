from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_at', 'due_date')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description')
        }),
        ('Статус и сроки', {
            'fields':('status', 'due_date')
        }),
        ('Метаданные', {
            'fields':('created_at', 'updated_at'),
            'classes':('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')