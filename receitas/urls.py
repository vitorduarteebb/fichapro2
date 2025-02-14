from django.urls import path
from . import views

app_name = 'receitas'

urlpatterns = [
    path('cadastro/<int:restaurante_id>/', views.receita_cadastro, name='receita_cadastro'),
    path('excluir/<int:pk>/', views.excluir_receita, name='excluir_receita'),
    path('detalhe/<int:receita_id>/', views.detalhe_receita, name='detalhe_receita'),
    path('api/detalhe/<int:receita_id>/', views.api_detalhe_receita, name='api_detalhe_receita'),
    path('atualizar-valor-trabalhado/<int:receita_id>/', views.atualizar_valor_trabalhado, name='atualizar_valor_trabalhado'),
    path('editar/<int:receita_id>/', views.editar_receita, name='editar_receita'),
]
