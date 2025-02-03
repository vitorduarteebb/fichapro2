from django import forms
from .models import Insumo

class ImportXMLForm(forms.Form):
    xml_file = forms.FileField(label="Selecione o arquivo XML")

class InsumoForm(forms.ModelForm):
    class Meta:
        model = Insumo
        fields = ['nome', 'unidade_medida', 'quantidade', 'preco', 'peso']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Digite o nome do insumo'
            }),
            'unidade_medida': forms.Select(attrs={
                'class': 'form-control'
            }),
            'quantidade': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Quantidade'
            }),
            'preco': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Preço'
            }),
            'peso': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Peso (automático para kg/g)'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        unidade = cleaned_data.get('unidade_medida')
        quantidade = cleaned_data.get('quantidade')
        # Se a unidade for kg ou g, forçamos o peso a ser igual à quantidade.
        if unidade in ['kg', 'g'] and quantidade is not None:
            cleaned_data['peso'] = quantidade
        return cleaned_data

# Nova classe que ignora a validação de unicidade do nome para importação:
class ImportInsumoForm(InsumoForm):
    def validate_unique(self):
        # Ignora a validação de unicidade para o processo de importação
        pass
