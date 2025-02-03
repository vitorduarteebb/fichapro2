from django.urls import path
from .views import receita_cadastro, excluir_receita

app_name = 'receitas'

urlpatterns = [
    path('cadastro/<int:restaurante_id>/', receita_cadastro, name='receita_cadastro'),
    path('excluir/<int:pk>/', excluir_receita, name='excluir_receita'),
]
