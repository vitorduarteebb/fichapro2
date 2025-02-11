from django.urls import path
from . import views

app_name = 'restaurante'

urlpatterns = [
    path('cadastro/', views.cadastro_restaurante, name='cadastro_restaurante'),
    path('lista/', views.lista_restaurantes, name='lista_restaurantes'),
    path('<int:pk>/', views.restaurante_detail, name='restaurante_detail'),
    path('editar/<int:pk>/', views.restaurante_edit, name='restaurante_edit'),
    path('excluir/<int:pk>/', views.excluir_restaurante, name='excluir_restaurante'),
    path('dashboard/<int:pk>/', views.visualizacao_dashboard, name='dashboard'),
]
