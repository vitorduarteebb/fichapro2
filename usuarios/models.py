from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class Usuario(AbstractUser):
    # Evita conflito de acesso reverso com o modelo `auth.User`
    groups = models.ManyToManyField(
        Group,
        related_name="usuario_groups",  # Definir um nome único
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="usuario_permissions",  # Definir um nome único
        blank=True
    )

    def __str__(self):
        return self.username
