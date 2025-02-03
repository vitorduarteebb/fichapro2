from django.urls import path
from .views import home

urlpatterns = [
    path('', home, name='home'),  # Página inicial do sistema
]
