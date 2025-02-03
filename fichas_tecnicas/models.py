from django.db import models
from decimal import Decimal
from insumos.models import Insumo
from restaurante.models import Restaurante
from receitas.models import Receita  # para selecionar receitas

class FichaTecnica(models.Model):
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE, related_name='fichas_tecnicas')
    nome_prato = models.CharField("Nome do Prato", max_length=255, default="Ficha Técnica sem nome")
    imagem = models.ImageField("Imagem do Prato", upload_to='fichas_tecnicas_imagens/', blank=True, null=True)
    porcao_sugerida = models.DecimalField("Porção Sugerida (em gramas)", max_digits=10, decimal_places=2)
    tempo_preparo = models.IntegerField("Tempo de Preparo (minutos)")
    modo_preparo = models.TextField("Modo de Preparo", blank=True)
    peso_total = models.DecimalField("Peso Total da Preparação (g)", max_digits=10, decimal_places=2, blank=True, null=True)
    custo_total_insumos = models.DecimalField("Custo Total dos Insumos (R$)", max_digits=10, decimal_places=2, blank=True, null=True)
    custo_total_receitas = models.DecimalField("Custo Total das Receitas (R$)", max_digits=10, decimal_places=2, blank=True, null=True)
    valor_venda_sugerida = models.DecimalField("Valor de Venda Sugerida (R$)", max_digits=10, decimal_places=2, blank=True, null=True)
    data_criacao = models.DateTimeField("Data de Cadastro", auto_now_add=True)

    def __str__(self):
        return self.nome_prato

class FichaTecnicaInsumo(models.Model):
    ficha_tecnica = models.ForeignKey(FichaTecnica, on_delete=models.CASCADE, related_name='itens_insumos')
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE)
    quantidade_utilizada = models.DecimalField(
        "Quantidade Utilizada", max_digits=10, decimal_places=2,
        help_text="Informe a quantidade utilizada (na mesma unidade do insumo)"
    )
    custo_utilizado = models.DecimalField("Custo Utilizado (R$)", max_digits=10, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Supondo que a quantidade utilizada já esteja na mesma unidade cadastrada no insumo.
        if self.insumo.preco and self.quantidade_utilizada:
            self.custo_utilizado = self.quantidade_utilizada * self.insumo.preco
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.insumo.nome} - {self.quantidade_utilizada}"

class FichaTecnicaReceita(models.Model):
    ficha_tecnica = models.ForeignKey(FichaTecnica, on_delete=models.CASCADE, related_name='itens_receitas')
    receita = models.ForeignKey(Receita, on_delete=models.CASCADE)
    quantidade_utilizada = models.DecimalField(
        "Quantidade Utilizada", max_digits=10, decimal_places=2,
        help_text="Informe a quantidade utilizada da receita na ficha (na unidade escolhida)"
    )
    unidade = models.CharField("Unidade", max_length=10, default="g")  # ex: 'kg', 'g', 'ml'
    custo_utilizado = models.DecimalField("Custo Utilizado (R$)", max_digits=10, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        # O custo é calculado com base no preço KG da receita.
        # Converter a quantidade para kg: se a unidade for 'g', divide por 1000; se 'kg', usa diretamente.
        if self.receita.preco_kg and self.quantidade_utilizada:
            if self.unidade.lower() == 'g':
                qt_kg = self.quantidade_utilizada / Decimal("1000")
            else:
                qt_kg = self.quantidade_utilizada
            self.custo_utilizado = (qt_kg * self.receita.preco_kg).quantize(Decimal("0.01"))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.receita.nome_prato} - {self.quantidade_utilizada} {self.unidade}"
