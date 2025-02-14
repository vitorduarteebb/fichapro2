from django import forms
from django.forms.models import BaseModelFormSet
from .models import Insumo

# Formset customizado para forçar a inclusão do campo DELETE mesmo em formulários extras
class BaseInsumoFormSet(BaseModelFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)
        if 'DELETE' not in form.fields:
            form.fields['DELETE'] = forms.BooleanField(required=False, widget=forms.HiddenInput)

class MultipleFileInput(forms.FileInput):
    allow_multiple_selected = True

    def render(self, name, value, attrs=None, renderer=None):
        attrs = attrs or {}
        attrs.setdefault('multiple', True)
        return super().render(name, value, attrs, renderer)

    def value_from_datadict(self, data, files, name):
        return files.getlist(name)

class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def to_python(self, data):
        if not data:
            return []
        return data

    def validate(self, value):
        if self.required and not value:
            raise forms.ValidationError(self.error_messages['required'])
        super().validate(value)

class ImportXMLForm(forms.Form):
    xml_file = MultipleFileField(
        label="Selecione os arquivos XML",
        error_messages={'required': 'Selecione pelo menos um arquivo XML.'}
    )

class InsumoForm(forms.ModelForm):
    class Meta:
        model = Insumo
        fields = ['nome', 'unidade_medida', 'quantidade', 'preco', 'peso']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome do insumo'
            }),
            'unidade_medida': forms.Select(attrs={'class': 'form-control'}),
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
        if unidade in ['kg', 'g'] and quantidade is not None:
            cleaned_data['peso'] = quantidade
        return cleaned_data

class ImportInsumoForm(InsumoForm):
    def __init__(self, *args, **kwargs):
        """
        Armazena o valor 'duplicado' (se passado via initial) para uso no template.
        """
        super().__init__(*args, **kwargs)
        self.duplicado = self.initial.get('duplicado', False)

    def validate_unique(self):
        # Ignora a validação de unicidade durante a importação
        pass
