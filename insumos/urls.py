from django.urls import path
from .views import (
    cadastro_insumo, lista_insumos, import_insumos, confirmar_import_insumos,
    excluir_insumo, editar_insumo, detalhe_insumo
)

app_name = 'insumos'

urlpatterns = [
    path('cadastro/<int:restaurante_id>/', cadastro_insumo, name='cadastro_insumo'),
    path('lista/', lista_insumos, name='lista_insumos'),
    path('importar/<int:restaurante_id>/', import_insumos, name='import_insumos'),
    path('importar/confirmar/', confirmar_import_insumos, name='confirmar_import_insumos'),
    path('excluir/<int:pk>/', excluir_insumo, name='excluir_insumo'),
    path('detalhe/<int:insumo_id>/', detalhe_insumo, name='detalhe_insumo'),
    path('editar/<int:insumo_id>/', editar_insumo, name='editar_insumo'),
]
