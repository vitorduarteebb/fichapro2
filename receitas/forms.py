from django import forms
from decimal import Decimal
from .models import Receita, ReceitaInsumo

AJUSTE_CHOICES = (
    ('none', 'Sem ajuste'),
    ('fc', 'FATOR DE CORREÇÃO IC'),
    ('ipc', 'IPC'),
)

class ReceitaForm(forms.ModelForm):
    class Meta:
        model = Receita
        fields = ['nome_prato', 'imagem', 'porcao_sugerida', 'tempo_preparo', 'modo_preparo']
        widgets = {
            'nome_prato': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Prato'}),
            'imagem': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'porcao_sugerida': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Porção (g)'}),
            'tempo_preparo': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Tempo (min)'}),
            'modo_preparo': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Modo de Preparo', 'rows': 5}),
        }

class ReceitaInsumoForm(forms.ModelForm):
    # Campo transitório para definir a unidade utilizada (para conversão)
    unidade = forms.ChoiceField(
        choices=[('kg', 'kg'), ('g', 'g'), ('L', 'L'), ('ml', 'ml')],
        initial='kg',
        label="Unid"
    )
    ajuste_tipo = forms.ChoiceField(
        choices=AJUSTE_CHOICES,
        widget=forms.RadioSelect,
        required=False,
        initial='none',
        label="Tipo"
    )
    ajuste_sinal = forms.ChoiceField(
        choices=(('mais', '+'), ('menos', '–')),
        widget=forms.RadioSelect,
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
        model = ReceitaInsumo
        fields = ['insumo', 'quantidade_utilizada', 'unidade', 'ajuste_tipo', 'ajuste_sinal', 'ajuste_percentual']
        widgets = {
            'insumo': forms.Select(attrs={'class': 'form-control insumo-select'}),
            'quantidade_utilizada': forms.NumberInput(attrs={'class': 'form-control quantidade-input', 'placeholder': 'Qtd'}),
        }
