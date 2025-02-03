from django.urls import path
from .views import ficha_tecnica_cadastro, excluir_ficha_tecnica

app_name = 'fichas_tecnicas'

urlpatterns = [
    path('cadastro/<int:restaurante_id>/', ficha_tecnica_cadastro, name='ficha_tecnica_cadastro'),
    path('excluir/<int:pk>/', excluir_ficha_tecnica, name='excluir_ficha_tecnica'),
]
