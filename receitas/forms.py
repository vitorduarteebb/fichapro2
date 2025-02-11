from django import forms
from .models import Receita, ReceitaInsumo

class ReceitaForm(forms.ModelForm):
    class Meta:
        model = Receita
        fields = ['nome_prato', 'imagem', 'porcao_sugerida', 'tempo_preparo', 'modo_preparo']
        widgets = {
            'nome_prato': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Prato'}),
            'imagem': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'porcao_sugerida': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Porção Sugerida (g)'}),
            'tempo_preparo': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Tempo de Preparo (min)'}),
            'modo_preparo': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Modo de Preparo (Passo a Passo)', 'rows': 5}),
        }

class ReceitaInsumoForm(forms.ModelForm):
    # Mesmo que a unidade seja selecionada, a lógica assume que o preço é informado por grama (se a unidade for "g")
    unidade = forms.ChoiceField(
        choices=[('kg', 'kg'), ('g', 'g'), ('L', 'L'), ('ml', 'ml')],
        initial='g',
        label="Unidade"
    )
    class Meta:
        model = ReceitaInsumo
        fields = ['insumo', 'quantidade_utilizada', 'unidade']
        widgets = {
            'insumo': forms.Select(attrs={'class': 'form-control insumo-select'}),
            'quantidade_utilizada': forms.NumberInput(attrs={'class': 'form-control quantidade-input', 'placeholder': 'Quantidade Utilizada'}),
        }
