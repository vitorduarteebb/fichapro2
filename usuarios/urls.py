from django.urls import path
from .views import login_view, dashboard_view, gerenciamento_usuarios, cadastrar_usuario, editar_usuario, excluir_usuario

app_name = "usuarios"

urlpatterns = [
    path("login/", login_view, name="login"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("gerenciar/", gerenciamento_usuarios, name="gerenciamento_usuarios"),
    path("cadastrar/", cadastrar_usuario, name="cadastrar_usuario"),
    path("editar/<int:pk>/", editar_usuario, name="editar_usuario"),
    path("excluir/<int:pk>/", excluir_usuario, name="excluir_usuario"),
]
