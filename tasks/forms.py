from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'duedate']  # если duedate в модели
        widgets = {
            'duedate': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
