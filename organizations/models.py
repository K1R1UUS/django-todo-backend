from django.db import models
from django.contrib.auth.models import User


class Branch(models.Model):
    """Филиал компании."""
    name = models.CharField(max_length=200, verbose_name="Название филиала")
    head = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="headed_branch",
        verbose_name="Начальник филиала",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Филиал"
        verbose_name_plural = "Филиалы"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Department(models.Model):
    """Отдел внутри филиала."""
    name = models.CharField(max_length=200, verbose_name="Название отдела")
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name="departments",
        verbose_name="Филиал",
    )
    head = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="headed_department",
        verbose_name="Начальник отдела",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Отдел"
        verbose_name_plural = "Отделы"
        ordering = ["branch", "name"]
        constraints = [
            models.UniqueConstraint(fields=["branch", "name"], name="unique_department_per_branch")
        ]

    def __str__(self):
        return f"{self.name} ({self.branch.name})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.head_id:
            Profile.objects.update_or_create(
                user_id=self.head_id,
                defaults={"department": self},
            )

class Profile(models.Model):
    """Расширение User — привязка сотрудника к отделу."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Пользователь",
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees",
        verbose_name="Отдел",
    )
    position = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Должность",
    )

    class Meta:
        verbose_name = "Профиль сотрудника"
        verbose_name_plural = "Профили сотрудников"

    def __str__(self):
        if self.position:
            return f"{self.user.username} — {self.position}"
        return self.user.username