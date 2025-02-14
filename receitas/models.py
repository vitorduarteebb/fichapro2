from django.db import models
from decimal import Decimal
from insumos.models import Insumo
from restaurante.models import Restaurante

def calculate_final_cost(insumo, quantidade_utilizada, unit_used, ajuste_tipo=None, ajuste_sinal='mais', ajuste_percentual=Decimal("0")):
    # Custo base: (quantidade_utilizada * insumo.preco) / insumo.quantidade
    base_cost = (quantidade_utilizada * insumo.preco) / Decimal(insumo.quantidade)
    if ajuste_tipo == 'fc' and ajuste_percentual > 0:
        if ajuste_sinal == 'mais':
            return base_cost * (1 + ajuste_percentual/Decimal("100"))
        else:
            return base_cost * (1 - ajuste_percentual/Decimal("100"))
    elif ajuste_tipo == 'ipc' and ajuste_percentual > 0:
        return base_cost * (100 / ajuste_percentual)
    else:
        return base_cost

class Receita(models.Model):
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE, related_name='receitas')
    nome_prato = models.CharField("NOME DO PRATO", max_length=255, default="RECEITA SEM NOME")
    imagem = models.ImageField("IMAGEM DO PRATO", upload_to='receitas_imagens/', blank=True, null=True)
    porcao_sugerida = models.DecimalField("PORÇÃO SUGERIDA (EM G)", max_digits=10, decimal_places=2)
    tempo_preparo = models.IntegerField("TEMPO DE PREPARO (MIN)")
    modo_preparo = models.TextField("MODO DE PREPARO", blank=True)
    peso_total = models.DecimalField("PESO TOTAL DA PREPARAÇÃO (G)", max_digits=10, decimal_places=2, blank=True, null=True)
    custo_total = models.DecimalField("CUSTO TOTAL DA RECEITA (R$)", max_digits=10, decimal_places=2, blank=True, null=True)
    preco_kg = models.DecimalField("PREÇO DO KG (R$)", max_digits=10, decimal_places=2, blank=True, null=True)
    valor_trabalhado = models.DecimalField("VALOR TRABALHADO (R$)", max_digits=10, decimal_places=2, blank=True, null=True)
    data_criacao = models.DateTimeField("DATA DE CADASTRO", auto_now_add=True)
    
    def rendimento(self):
        if self.peso_total and self.porcao_sugerida and self.porcao_sugerida > 0:
            return self.peso_total / self.porcao_sugerida
        return None

    def __str__(self):
        return self.nome_prato

class ReceitaInsumo(models.Model):
    receita = models.ForeignKey(Receita, on_delete=models.CASCADE, related_name='itens')
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE)
    quantidade_utilizada = models.DecimalField("QUANTIDADE UTILIZADA", max_digits=10, decimal_places=2,
                                                 help_text="Informe a quantidade utilizada (na mesma unidade do insumo)")
    ajuste_tipo = models.CharField(max_length=10, blank=True, null=True,
                                   help_text="Tipo de ajuste: 'fc' para FATOR DE CORREÇÃO IC, 'ipc' para IPC ou vazio")
    ajuste_sinal = models.CharField(max_length=10, blank=True, null=True,
                                    help_text="Sinal de ajuste: 'mais' ou 'menos'")
    ajuste_percentual = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True,
                                              help_text="Valor percentual do ajuste")
    custo_utilizado = models.DecimalField("CUSTO UTILIZADO (R$)", max_digits=10, decimal_places=2, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        # 'unit_used' é definido no view via campo transitório; se não existir, usa a unidade do insumo.
        unit_used = getattr(self, 'unit_used', self.insumo.unidade_medida)
        final_cost = calculate_final_cost(
            self.insumo,
            self.quantidade_utilizada,
            unit_used,
            ajuste_tipo=self.ajuste_tipo if self.ajuste_tipo not in [None, '', 'none'] else None,
            ajuste_sinal=self.ajuste_sinal or 'mais',
            ajuste_percentual=self.ajuste_percentual or Decimal("0")
        )
        self.custo_utilizado = final_cost.quantize(Decimal("0.01"))
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.insumo.nome} - {self.quantidade_utilizada}"
