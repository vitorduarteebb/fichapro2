from django import forms
from .models import FichaTecnica, FichaTecnicaInsumo, FichaTecnicaReceita
from decimal import Decimal
class FichaTecnicaForm(forms.ModelForm):
    class Meta:
        model = FichaTecnica
        fields = ['nome_prato', 'imagem', 'porcao_sugerida', 'tempo_preparo', 'modo_preparo']
        widgets = {
            'nome_prato': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Prato'}),
            'imagem': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'porcao_sugerida': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Porção Sugerida (g)'}),
            'tempo_preparo': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Tempo de Preparo (min)'}),
            'modo_preparo': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Modo de Preparo (Passo a Passo)', 'rows': 5}),
        }

class FichaTecnicaInsumoForm(forms.ModelForm):
    # Campo para selecionar a unidade usada (kg ou g)
    unidade = forms.ChoiceField(
        choices=[('kg', 'kg'), ('g', 'g')],
        initial='kg',
        label="Unidade"
    )
    # Escolhas para o tipo de ajuste – IC é representado por 'fc'
    AJUSTE_CHOICES = (
        ('none', 'Sem ajuste'),
        ('fc', 'IC'),
        ('ipc', 'IPC'),
    )
    ajuste_tipo = forms.ChoiceField(
        choices=AJUSTE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control ajuste-tipo'}),
        required=False,
        initial='none',
        label="Tipo de Ajuste"
    )
    ajuste_sinal = forms.ChoiceField(
        choices=(('mais', '+'), ('menos', '–')),
        widget=forms.Select(attrs={'class': 'form-control ajuste-sinal'}),
        required=False,
        initial='mais',
        label="Sinal"
    )
    ajuste_percentual = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        min_value=0,
        max_value=100,
        label="Perc (%)"
    )
    class Meta:
        model = FichaTecnicaInsumo
        fields = ['insumo', 'quantidade_utilizada', 'unidade', 'ajuste_tipo', 'ajuste_sinal', 'ajuste_percentual']
        widgets = {
            'insumo': forms.Select(attrs={'class': 'form-control insumo-select'}),
            'quantidade_utilizada': forms.NumberInput(attrs={'class': 'form-control quantidade-input', 'placeholder': 'Quantidade Utilizada'}),
        }
    # Campo para selecionar a unidade usada (kg ou g)
    unidade = forms.ChoiceField(
        choices=[('kg', 'kg'), ('g', 'g')],
        initial='kg',
        label="Unidade"
    )
    # Escolhas para o tipo de ajuste – IC é representado por 'fc'
    AJUSTE_CHOICES = (
        ('none', 'Sem ajuste'),
        ('fc', 'IC'),
        ('ipc', 'IPC'),
    )
    ajuste_tipo = forms.ChoiceField(
        choices=[('none', 'Sem ajuste'), ('fc', 'IC'), ('ipc', 'IPC')],
        widget=forms.Select(attrs={'class': 'form-control ajuste-tipo'}),
        required=False,
        initial='none',
        label="Tipo de Ajuste"
    )
    ajuste_sinal = forms.ChoiceField(
        choices=[('mais', '+'), ('menos', '–')],
        widget=forms.Select(attrs={'class': 'form-control ajuste-sinal'}),
        required=False,
        initial='mais',
        label="Sinal"
    )
    ajuste_percentual = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        min_value=0,
        max_value=100,
        label="Perc (%)"
    )
    class Meta:
        model = FichaTecnicaInsumo
        fields = ['insumo', 'quantidade_utilizada', 'unidade', 'ajuste_tipo', 'ajuste_sinal', 'ajuste_percentual']
        widgets = {
            'insumo': forms.Select(attrs={'class': 'form-control insumo-select'}),
            'quantidade_utilizada': forms.NumberInput(attrs={'class': 'form-control quantidade-input', 'placeholder': 'Quantidade Utilizada'}),
        }

class FichaTecnicaReceitaForm(forms.ModelForm):
    UNIDADE_CHOICES = [
        ('kg', 'kg'),
        ('g', 'g'),
        ('L', 'L'),
        ('ml', 'ml'),
    ]
    unidade = forms.ChoiceField(choices=UNIDADE_CHOICES, initial='kg', label="Unidade")
    class Meta:
        model = FichaTecnicaReceita
        fields = ['receita', 'quantidade_utilizada', 'unidade']
        widgets = {
            'receita': forms.Select(attrs={'class': 'form-control receita-select'}),
            'quantidade_utilizada': forms.NumberInput(attrs={'class': 'form-control quantidade-input', 'placeholder': 'Quantidade Utilizada'}),
        }
            