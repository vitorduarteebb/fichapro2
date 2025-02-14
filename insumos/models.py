from django.db import models
from restaurante.models import Restaurante

class Insumo(models.Model):
    UNIDADES = (
        ('unidade', 'Unidade'),
        ('caixa', 'Caixa'),
        ('kg', 'Quilograma'),
        ('g', 'Grama'),
        ('ml', 'Mililitro'),
        ('l', 'Litro'),
    )

    restaurante = models.ForeignKey(
        Restaurante,
        on_delete=models.CASCADE,
        related_name="insumos",
        verbose_name="Restaurante",
        null=True,
        blank=True
    )
    nome = models.CharField(max_length=100)
    unidade_medida = models.CharField(max_length=20, choices=UNIDADES)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    peso = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        unique_together = (("restaurante", "nome"),)

    def save(self, *args, **kwargs):
        if self.unidade_medida in ['kg', 'g']:
            self.peso = self.quantidade
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome
