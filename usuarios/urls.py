from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    login_view, dashboard_view, gerenciamento_usuarios,
    cadastrar_usuario, editar_usuario, excluir_usuario, perfil_view,
    editar_perfil_view  # nova view para editar perfil
)

app_name = "usuarios"

urlpatterns = [
    path("login/", login_view, name="login"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("gerenciar/", gerenciamento_usuarios, name="gerenciamento_usuarios"),
    path("cadastrar/", cadastrar_usuario, name="cadastrar_usuario"),
    path("editar/<int:pk>/", editar_usuario, name="editar_usuario"),
    path("excluir/<int:pk>/", excluir_usuario, name="excluir_usuario"),
    path("perfil/", perfil_view, name="perfil"),
    path("editar-perfil/", editar_perfil_view, name="editar_perfil"),  # nova URL
    path("alterar-senha/", auth_views.PasswordChangeView.as_view(
        template_name="usuarios/alterar_senha.html",
        success_url="/usuarios/dashboard/"  # ou use reverse_lazy("usuarios:dashboard")
    ), name="alterar_senha"),
    path("logout/", auth_views.LogoutView.as_view(next_page="usuarios:login"), name="logout"),
]
