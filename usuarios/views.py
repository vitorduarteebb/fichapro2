from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                # Recupera o parâmetro "next", se houver, para redirecionamento
                next_url = request.GET.get("next") or request.POST.get("next")
                # Se for Admin ou Superusuário, direciona para o dashboard
                if user.role == "admin" or user.is_superuser:
                    return redirect(next_url or "usuarios:dashboard")
                else:
                    # Para Standard e Master, redireciona para o restaurante vinculado
                    if user.restaurante:
                        return redirect(next_url or reverse("restaurante:restaurante_detail", kwargs={"pk": user.restaurante.id}))
                    else:
                        # Se não houver restaurante, redireciona para uma página padrão
                        return redirect(next_url or "home")
            else:
                messages.error(request, "Sua conta está inativa. Entre em contato com o administrador.")
        else:
            messages.error(request, "Usuário ou senha incorretos!")
    return render(request, "usuarios/login.html")

@login_required
def dashboard_view(request):
    return render(request, "usuarios/dashboard.html")

@login_required
def gerenciamento_usuarios(request):
    """
    Se o usuário for Admin, exibe todos os usuários; caso contrário, apenas os usuários do mesmo restaurante.
    """
    if request.user.role == "admin":
        usuarios = CustomUser.objects.all()
    else:
        usuarios = CustomUser.objects.filter(restaurante=request.user.restaurante)
    return render(request, "usuarios/gerenciamento_usuarios.html", {"usuarios": usuarios})

@login_required
def cadastrar_usuario(request):
    # Apenas Admin pode criar usuários
    if request.user.role != "admin":
        raise PermissionDenied("Você não tem permissão para cadastrar usuários.")
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuário cadastrado com sucesso!")
            return redirect("usuarios:gerenciamento_usuarios")
    else:
        form = CustomUserCreationForm()
    return render(request, "usuarios/cadastro_usuario.html", {"form": form})

@login_required
def editar_usuario(request, pk):
    # Apenas Admin pode editar usuários
    if request.user.role != "admin":
        raise PermissionDenied("Você não tem permissão para editar usuários.")
    usuario = get_object_or_404(CustomUser, pk=pk)
    if request.method == "POST":
        form = CustomUserChangeForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuário atualizado com sucesso!")
            return redirect("usuarios:gerenciamento_usuarios")
    else:
        form = CustomUserChangeForm(instance=usuario)
    return render(request, "usuarios/cadastro_usuario.html", {"form": form})

@login_required
def excluir_usuario(request, pk):
    # Apenas Admin pode excluir usuários
    if request.user.role != "admin":
        raise PermissionDenied("Você não tem permissão para excluir usuários.")
    usuario = get_object_or_404(CustomUser, pk=pk)
    if request.method == "POST":
        usuario.delete()
        messages.success(request, "Usuário excluído com sucesso!")
        return redirect("usuarios:gerenciamento_usuarios")
    return render(request, "usuarios/confirmar_exclusao.html", {"usuario": usuario})
