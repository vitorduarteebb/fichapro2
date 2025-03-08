from django.db import models
from decimal import Decimal, ROUND_HALF_UP
from restaurante.models import Restaurante
from receitas.models import Receita

def calculate_final_cost_ficha(insumo, quantidade_utilizada, ajuste_tipo=None, ajuste_sinal='mais', ajuste_percentual=Decimal("0")):
    base_cost = (quantidade_utilizada * insumo.preco) / Decimal(insumo.quantidade)
    if ajuste_tipo == 'fc' and ajuste_percentual > 0:
        if ajuste_sinal == 'mais':
            return base_cost * (1 + ajuste_percentual / Decimal("100"))
        else:
            return base_cost * (1 - ajuste_percentual / Decimal("100"))
    elif ajuste_tipo == 'ipc' and ajuste_percentual > 0:
        # Se apenas X% do insumo é aproveitado, o custo aumenta proporcionalmente.
        return base_cost * (Decimal("100") / ajuste_percentual)
    else:
        return base_cost

class FichaTecnica(models.Model):
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE, related_name='fichas_tecnicas')
    nome_prato = models.CharField("NOME DO PRATO", max_length=255, default="FICHA TÉCNICA SEM NOME")
    imagem = models.ImageField("IMAGEM DO PRATO", upload_to='fichas_tecnicas_imagens/', blank=True, null=True)
    porcao_sugerida = models.DecimalField("PORÇÃO SUGERIDA (EM GRAMAS)", max_digits=10, decimal_places=2)
    tempo_preparo = models.IntegerField("TEMPO DE PREPARO (MIN)")
    modo_preparo = models.TextField("MODO DE PREPARO", blank=True)
    peso_total = models.DecimalField("PESO TOTAL DA PREPARAÇÃO (G)", max_digits=10, decimal_places=2, blank=True, null=True)
    custo_total_insumos = models.DecimalField("CUSTO TOTAL DOS INSUMOS (R$)", max_digits=10, decimal_places=2, blank=True, null=True)
    custo_total_receitas = models.DecimalField("CUSTO TOTAL DAS RECEITAS (R$)", max_digits=10, decimal_places=2, blank=True, null=True)
    valor_venda_sugerida = models.DecimalField("VALOR DE VENDA SUGERIDA (R$)", max_digits=10, decimal_places=2, blank=True, null=True)
    valor_trabalhado = models.DecimalField("VALOR TRABALHADO (R$)", max_digits=10, decimal_places=2, blank=True, null=True)
    data_criacao = models.DateTimeField("DATA DE CADASTRO", auto_now_add=True)

    def __str__(self):
        return self.nome_prato

class FichaTecnicaInsumo(models.Model):
    ficha_tecnica = models.ForeignKey(FichaTecnica, on_delete=models.CASCADE, related_name='itens_insumos')
    insumo = models.ForeignKey('insumos.Insumo', on_delete=models.CASCADE)
    quantidade_utilizada = models.DecimalField("QUANTIDADE UTILIZADA", max_digits=10, decimal_places=2,
                                                 help_text="Informe a quantidade utilizada (na mesma unidade do insumo)")
    ajuste_tipo = models.CharField("TIPO DE AJUSTE", max_length=10, blank=True, null=True,
                                   help_text="Informe 'fc' para IC ou 'ipc' para IPC")
    ajuste_sinal = models.CharField("SINAL DO AJUSTE", max_length=10, blank=True, null=True,
                                    help_text="Informe 'mais' ou 'menos'")
    ajuste_percentual = models.DecimalField("PERCENTUAL DE AJUSTE (%)", max_digits=5, decimal_places=2, blank=True, null=True,
                                              help_text="Ex.: 70 para 70%")
    custo_utilizado = models.DecimalField("CUSTO UTILIZADO (R$)", max_digits=10, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.insumo.preco and self.insumo.quantidade and self.quantidade_utilizada:
            final_cost = calculate_final_cost_ficha(
                self.insumo,
                self.quantidade_utilizada,
                ajuste_tipo=self.ajuste_tipo if self.ajuste_tipo not in [None, '', 'none'] else None,
                ajuste_sinal=self.ajuste_sinal or 'mais',
                ajuste_percentual=self.ajuste_percentual or Decimal("0")
            )
            self.custo_utilizado = final_cost.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.insumo.nome} - {self.quantidade_utilizada}"

class FichaTecnicaReceita(models.Model):
    ficha_tecnica = models.ForeignKey(FichaTecnica, on_delete=models.CASCADE, related_name='itens_receitas')
    receita = models.ForeignKey(Receita, on_delete=models.CASCADE)
    quantidade_utilizada = models.DecimalField("QUANTIDADE UTILIZADA", max_digits=10, decimal_places=2,
                                                 help_text="Informe a quantidade utilizada da receita na ficha (na unidade escolhida)")
    unidade = models.CharField("UNIDADE", max_length=10, default="g")
    custo_utilizado = models.DecimalField("CUSTO UTILIZADO (R$)", max_digits=10, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.receita.preco_kg and self.quantidade_utilizada:
            if self.unidade.lower() == 'g':
                qt_kg = self.quantidade_utilizada / Decimal("1000")
            else:
                qt_kg = self.quantidade_utilizada
            self.custo_utilizado = (qt_kg * self.receita.preco_kg).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.receita.nome_prato} - {self.quantidade_utilizada} {self.unidade}"
