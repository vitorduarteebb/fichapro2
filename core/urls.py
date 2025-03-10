from django.urls import path
from .views import home, search_results_view  # Certifique-se de que search_results_view está sendo importada

urlpatterns = [
    path('', home, name='home'),  # Página inicial do sistema
    path('search/', search_results_view, name='search_results'),
]
