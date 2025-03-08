from django import forms
from .models import Restaurante

class FatorCorrecaoForm(forms.ModelForm):
    class Meta:
        model = Restaurante
        fields = ['fator_correcao_financeiro']
        widgets = {
            'fator_correcao_financeiro': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class RestauranteForm(forms.ModelForm):
    class Meta:
        model = Restaurante
        fields = [
            'tipo_pessoa', 
            # Pessoa Jurídica
            'cnpj', 'nome_restaurante', 'inscricao_estadual', 'inscricao_municipal',
            # Pessoa Física
            'nome', 'cpf', 'rg',
            # Dados de contato e endereço
            'email', 'telefone', 'cep', 'endereco', 'numero', 'complemento', 'bairro', 'cidade', 'estado',
            'fator_correcao_financeiro',
            'logo'
        ]
        widgets = {
            'tipo_pessoa': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o CNPJ'}),
            'nome_restaurante': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Restaurante'}),
            'inscricao_estadual': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Inscrição Estadual'}),
            'inscricao_municipal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Inscrição Municipal'}),
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o seu Nome'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o CPF'}),
            'rg': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o RG'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Digite o E-mail'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o Telefone'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o CEP', 'required': 'required'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Endereço', 'readonly': 'readonly'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Complemento'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bairro', 'readonly': 'readonly'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cidade', 'readonly': 'readonly'}),
            'estado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Estado', 'readonly': 'readonly'}),
            'fator_correcao_financeiro': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Fator Correção Financeiro'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    class Meta:
        model = Restaurante
        fields = [
            'tipo_pessoa', 
            # Campos para Pessoa Jurídica
            'cnpj', 'nome_restaurante', 'inscricao_estadual', 'inscricao_municipal',
            # Campos para Pessoa Física
            'nome', 'cpf', 'rg',
            # Dados de contato
            'email', 'telefone', 
            # Endereço
            'cep', 'endereco', 'numero', 'complemento', 'bairro', 'cidade', 'estado',
            'fator_correcao_financeiro'
        ]
        widgets = {
            'tipo_pessoa': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o CNPJ'}),
            'nome_restaurante': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Restaurante'}),
            'inscricao_estadual': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Inscrição Estadual'}),
            'inscricao_municipal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Inscrição Municipal'}),
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o seu Nome'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o CPF'}),
            'rg': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o RG'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Digite o E-mail'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o Telefone'}),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o CEP', 'required': 'required'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Endereço', 'readonly': 'readonly'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Complemento'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bairro', 'readonly': 'readonly'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cidade', 'readonly': 'readonly'}),
            'estado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Estado', 'readonly': 'readonly'}),
            'fator_correcao_financeiro': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Fator Correção Financeiro'}),
        }
