from django.db import models

class Restaurante(models.Model):
    TIPO_PESSOA_CHOICES = [
        ('PF', 'Pessoa Física'),
        ('PJ', 'Pessoa Jurídica'),
    ]

    # Dados gerais
    tipo_pessoa = models.CharField(max_length=2, choices=TIPO_PESSOA_CHOICES)

    # Campos para Pessoa Jurídica (PJ)
    cnpj = models.CharField("CNPJ", max_length=20, blank=True, null=True)
    nome_restaurante = models.CharField("Nome do Restaurante", max_length=150, blank=True, null=True)
    inscricao_estadual = models.CharField("Inscrição Estadual", max_length=50, blank=True, null=True)
    inscricao_municipal = models.CharField("Inscrição Municipal", max_length=50, blank=True, null=True)

    # Campos para Pessoa Física (PF)
    cpf = models.CharField("CPF", max_length=14, blank=True, null=True)
    rg = models.CharField("RG", max_length=20, blank=True, null=True)

    # Dados de contato
    email = models.EmailField("E-mail", blank=True, null=True)
    telefone = models.CharField("Telefone", max_length=20, blank=True, null=True)

    # Endereço (campos obrigatórios: CEP, Endereço e Bairro)
    cep = models.CharField("CEP", max_length=9)
    endereco = models.CharField("Endereço", max_length=255)
    numero = models.CharField("Número", max_length=10, blank=True, null=True)
    complemento = models.CharField("Complemento", max_length=255, blank=True, null=True)
    bairro = models.CharField("Bairro", max_length=100)
    cidade = models.CharField("Cidade", max_length=100, blank=True, null=True)
    estado = models.CharField("Estado", max_length=2, blank=True, null=True)

    data_cadastro = models.DateTimeField("Data de Cadastro", auto_now_add=True)
    
    # Fator de Correção Financeiro
    fator_correcao_financeiro = models.DecimalField(
        "Fator Correção Financeiro",
        max_digits=10,
        decimal_places=2,
        default=1.00,
        blank=True,  # Permite que o campo seja deixado em branco no formulário
        help_text="Utilize esse fator para ajustes na precificação (ex: 1.00 = sem alteração, 1.10 = +10%)"
    )


    def __str__(self):
        if self.tipo_pessoa == 'PJ':
            return self.nome_restaurante or 'Restaurante sem nome'
        else:
            return self.cpf or 'Restaurante PF'


class RestauranteFile(models.Model):
    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE, related_name='arquivos')
    title = models.CharField(max_length=255, blank=True, null=True)
    file = models.FileField(upload_to='restaurante_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title if self.title else self.file.name
