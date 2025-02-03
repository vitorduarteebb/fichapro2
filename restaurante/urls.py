from django.urls import path
from .views import cadastro_restaurante, lista_restaurantes, restaurante_detail, restaurante_edit, excluir_restaurante

app_name = 'restaurante'

urlpatterns = [
    path('cadastro/', cadastro_restaurante, name='cadastro_restaurante'),
    path('lista/', lista_restaurantes, name='lista_restaurantes'),
    path('<int:pk>/', restaurante_detail, name='restaurante_detail'),
    path('editar/<int:pk>/', restaurante_edit, name='restaurante_edit'),
    path('excluir/<int:pk>/', excluir_restaurante, name='excluir_restaurante'),
]
