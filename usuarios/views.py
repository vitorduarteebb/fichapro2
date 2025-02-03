from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.is_superuser:
                return redirect("usuarios:dashboard")  # Aqui corrigimos a referência ao namespace correto
            else:
                return redirect("home")  # Se não for admin, vá para outra página
        else:
            messages.error(request, "Usuário ou senha incorretos!")

    return render(request, "usuarios/login.html")

@login_required
def dashboard_view(request):
    return render(request, "usuarios/dashboard.html")  # Certifique-se de que o caminho está correto
