from django.db import models
from django.utils import timezone
from decimal import Decimal
from insumos.models import Insumo
from restaurante.models import Restaurante

class Receita(models.Model):
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE, related_name='receitas')
    nome_prato = models.CharField("Nome do Prato", max_length=255, default="Receita sem nome")
    imagem = models.ImageField("Imagem do Prato", upload_to='receitas_imagens/', blank=True, null=True)
    porcao_sugerida = models.DecimalField("Porção Sugerida (em gramas)", max_digits=10, decimal_places=2)
    tempo_preparo = models.IntegerField("Tempo de Preparo (minutos)")
    modo_preparo = models.TextField("Modo de Preparo", blank=True)
    peso_total = models.DecimalField("Peso Total da Preparação (g)", max_digits=10, decimal_places=2, blank=True, null=True)
    custo_total = models.DecimalField("Custo Total da Receita (R$)", max_digits=10, decimal_places=2, blank=True, null=True)
    preco_kg = models.DecimalField("Preço do KG (R$)", max_digits=10, decimal_places=2, blank=True, null=True)
    data_criacao = models.DateTimeField("Data de Cadastro", auto_now_add=True)

    def rendimento(self):
        if self.peso_total and self.porcao_sugerida and self.porcao_sugerida > 0:
            return self.peso_total / self.porcao_sugerida
        return None

    def __str__(self):
        return self.nome_prato


class ReceitaInsumo(models.Model):
    receita = models.ForeignKey(Receita, on_delete=models.CASCADE, related_name='itens')
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE)
    quantidade_utilizada = models.DecimalField(
        "Quantidade Utilizada", max_digits=10, decimal_places=2,
        help_text="Informe a quantidade utilizada (na mesma unidade do insumo)"
    )
    # Este campo pode ser recalculado automaticamente
    custo_utilizado = models.DecimalField("Custo Utilizado (R$)", max_digits=10, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Calcula o custo proporcional baseado no preço do insumo e na quantidade utilizada.
        if self.insumo.preco and self.quantidade_utilizada:
            self.custo_utilizado = self.quantidade_utilizada * self.insumo.preco
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.insumo.nome} - {self.quantidade_utilizada}"
