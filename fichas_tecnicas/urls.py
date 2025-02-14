from django.urls import path
from . import views

app_name = 'fichas_tecnicas'

urlpatterns = [
    path('cadastro/<int:restaurante_id>/', views.ficha_tecnica_cadastro, name='ficha_tecnica_cadastro'),
    path('excluir/<int:pk>/', views.excluir_ficha_tecnica, name='excluir_ficha_tecnica'),
    path('detalhe/<int:ficha_id>/', views.detalhe_ficha_tecnica, name='detalhe_ficha'),
    path('editar/<int:ficha_id>/', views.editar_ficha_tecnica, name='editar_ficha_tecnica'),
    path('api/detalhe/<int:ficha_id>/', views.api_detalhe_ficha, name='api_detalhe_ficha'),
    path('atualizar-valor-trabalhado/<int:ficha_id>/', views.atualizar_valor_trabalhado, name='atualizar_valor_trabalhado'),
]
