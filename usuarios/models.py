from django.contrib.auth.models import AbstractUser
from django.db import models
from restaurante.models import Restaurante

USER_ROLE_CHOICES = (
    ('standard', 'Standard'),
    ('master', 'Master'),
    ('admin', 'Admin'),
)

class CustomUser(AbstractUser):
    role = models.CharField(
        max_length=10,
        choices=USER_ROLE_CHOICES,
        default='standard',
        verbose_name="Tipo de Usuário"
    )
    restaurante = models.ForeignKey(
        Restaurante,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Restaurante Vinculado",
        help_text="Vincule o usuário a um restaurante (apenas para Standard e Master)"
    )

    def __str__(self):
        return self.username
