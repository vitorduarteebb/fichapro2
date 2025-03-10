from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .forms import CustomUserCreationForm, CustomUserEditForm
from .models import CustomUser
from django.utils import timezone
from datetime import timedelta

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
    if request.user.role == "admin":
        usuarios = CustomUser.objects.all()
    else:
        usuarios = CustomUser.objects.filter(restaurante=request.user.restaurante)
    
    now = timezone.now()
    for usuario in usuarios:
        try:
            last_seen = usuario.profile.last_seen
        except AttributeError:
            last_seen = None
        if last_seen:
            delta = now - last_seen
            if delta <= timedelta(minutes=5):
                usuario.status_color = "green"
            elif delta <= timedelta(hours=1):
                usuario.status_color = "orange"
            else:
                usuario.status_color = "red"
        else:
            usuario.status_color = "red"
    
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
    if request.user.role != "admin":
        raise PermissionDenied("Você não tem permissão para editar usuários.")
    usuario = get_object_or_404(CustomUser, pk=pk)
    if request.method == "POST":
        form = CustomUserEditForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuário atualizado com sucesso!")
            return redirect("usuarios:gerenciamento_usuarios")
    else:
        form = CustomUserEditForm(instance=usuario)
    return render(request, "usuarios/cadastro_usuario.html", {"form": form})
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


@login_required
def perfil_view(request):
    return render(request, 'usuarios/perfil.html')


@login_required
def editar_perfil_view(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        bio = request.POST.get("bio")
        user = request.user

        if full_name:
            # Divide em primeiro e último nome se houver espaço; senão, atribui somente o primeiro nome.
            user.first_name, user.last_name = full_name.split(" ", 1) if " " in full_name else (full_name, "")
        if email:
            user.email = email
        user.save()

        # Atualiza os dados do perfil
        profile = None
        try:
            profile = user.profile
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=user)

        profile.bio = bio

        # Se houver upload de arquivo, atualiza a imagem
        if request.FILES.get("profile_image"):
            profile.image = request.FILES.get("profile_image")
        
        profile.save()
        return redirect("usuarios:perfil")
    
    return render(request, "usuarios/editar_perfil.html")