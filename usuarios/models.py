from django.contrib.auth.models import AbstractUser
from django.db import models
from restaurante.models import Restaurante
from django.db.models.signals import post_save
from django.dispatch import receiver

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


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField("Biografia", null=True, blank=True)
    image = models.ImageField(
        "Foto de Perfil", 
        upload_to='profile_images/', 
        null=True, 
        blank=True,
        max_length=255
    )
    last_seen = models.DateTimeField("Última vez online", null=True, blank=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"


@receiver(post_save, sender=CustomUser)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        try:
            instance.profile.save()
        except Profile.DoesNotExist:
            Profile.objects.create(user=instance)
