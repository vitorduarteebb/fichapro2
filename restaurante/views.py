from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from decimal import Decimal
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from restaurante.models import Restaurante
from restaurante.forms import RestauranteForm, FatorCorrecaoForm
from restaurante.models import Restaurante
from restaurante.forms import RestauranteForm, FatorCorrecaoForm


@login_required
def upload_logo(request, pk):
    restaurante = get_object_or_404(Restaurante, pk=pk)
    # Apenas Admin pode atualizar a logo
    if request.user.role != 'admin':
        raise PermissionDenied("Você não tem permissão para atualizar a logo.")
    if request.method == 'POST':
        if 'logo' in request.FILES:
            restaurante.logo = request.FILES['logo']
            restaurante.save()
            messages.success(request, "Logo atualizada com sucesso!")
        else:
            messages.error(request, "Nenhum arquivo enviado.")
    return redirect(reverse('restaurante:restaurante_detail', kwargs={'pk': restaurante.pk}))


@login_required
def cadastro_restaurante(request):
    # Apenas Admin pode cadastrar restaurantes.
    if request.user.role != 'admin':
        raise PermissionDenied("Você não tem permissão para cadastrar restaurantes.")
    
    if request.method == 'POST':
        form = RestauranteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('restaurante:lista_restaurantes'))
        else:
            print("Erros do formulário:", form.errors)
    else:
        form = RestauranteForm()
    return render(request, 'restaurante/cadastro_restaurante.html', {'form': form})

@login_required
def lista_restaurantes(request):
    # Se o usuário for Standard ou Master, ele vê somente o restaurante vinculado
    if request.user.role in ['standard', 'master']:
        restaurantes = Restaurante.objects.filter(id=request.user.restaurante.id)
    else:
        restaurantes = Restaurante.objects.all()
    return render(request, "restaurante/lista_restaurantes.html", {"restaurantes": restaurantes})

@login_required
def restaurante_detail(request, pk):
    # Obtém o restaurante ou retorna 404
    restaurante = get_object_or_404(Restaurante, pk=pk)
    
    # Se o usuário for standard ou master, verifica se ele tem um restaurante vinculado
    # e se o restaurante acessado é o mesmo do usuário.
    if request.user.role in ['standard', 'master']:
        if not getattr(request.user, 'restaurante', None) or restaurante.id != request.user.restaurante.id:
            raise PermissionDenied("Você não tem permissão para acessar este restaurante.")
    
    # Obtém os objetos relacionados – estes related_names devem estar configurados corretamente.
    receitas = restaurante.receitas.all()           # Ex: related_name="receitas" em Receita
    insumos = restaurante.insumos.all()               # Ex: related_name="insumos" em Insumo
    fichas_tecnicas = restaurante.fichas_tecnicas.all() # Ex: related_name="fichas_tecnicas" em FichaTecnica

    # Processa o formulário de atualização do fator de correção.
    # Apenas Admin pode atualizar este campo.
    if request.method == 'POST':
        fator_form = FatorCorrecaoForm(request.POST, instance=restaurante)
        if request.user.role == 'admin' and fator_form.is_valid():
            fator_form.save()
            return redirect(reverse('restaurante:restaurante_detail', kwargs={'pk': restaurante.pk}))
    else:
        fator_form = FatorCorrecaoForm(instance=restaurante)
    
    # Variável para exibir botões de ação: somente para admin.
    show_actions = (request.user.role == 'admin')
    # Variável para exibir os preços: apenas admin e master podem ver os preços.
    show_prices = (request.user.role in ['admin', 'master'])
    
    context = {
        'restaurante': restaurante,
        'receitas': receitas,
        'insumos': insumos,
        'fichas_tecnicas': fichas_tecnicas,
        'fator_form': fator_form,
        'show_actions': show_actions,
        'show_prices': show_prices,
    }
    return render(request, 'restaurante/restaurante_detail.html', context)
    # Busca o restaurante ou retorna 404
    restaurante = get_object_or_404(Restaurante, pk=pk)
    
    # Para usuários standard e master, apenas o restaurante vinculado pode ser acessado
    if request.user.role in ['standard', 'master']:
        if not request.user.restaurante or restaurante.id != request.user.restaurante.id:
            raise PermissionDenied("Você não tem permissão para acessar este restaurante.")
    
    # Obter dados relacionados (assegure-se de que os related_names estejam configurados corretamente)
    receitas = restaurante.receitas.all()
    insumos = restaurante.insumos.all()
    fichas_tecnicas = restaurante.fichas_tecnicas.all()
    
    # Processa o formulário de atualização do fator de correção.
    # Apenas Admin pode atualizar o fator.
    if request.method == 'POST':
        fator_form = FatorCorrecaoForm(request.POST, instance=restaurante)
        if request.user.role == 'admin' and fator_form.is_valid():
            fator_form.save()
            return redirect(reverse('restaurante:restaurante_detail', kwargs={'pk': restaurante.pk}))
    else:
        fator_form = FatorCorrecaoForm(instance=restaurante)
    
    # Define show_actions: somente Admin poderá ver os botões de ação
    show_actions = (request.user.role == 'admin')
    
    context = {
        'restaurante': restaurante,
        'receitas': receitas,
        'insumos': insumos,
        'fichas_tecnicas': fichas_tecnicas,
        'fator_form': fator_form,
        'show_actions': show_actions,
    }
    return render(request, 'restaurante/restaurante_detail.html', context)

@login_required
def restaurante_edit(request, pk):
    # Apenas Admin pode editar restaurantes.
    if request.user.role != 'admin':
        raise PermissionDenied("Você não tem permissão para editar restaurantes.")
    
    restaurante = get_object_or_404(Restaurante, pk=pk)
    if request.method == 'POST':
        form = RestauranteForm(request.POST, instance=restaurante)
        if form.is_valid():
            form.save()
            return redirect(reverse('restaurante:restaurante_detail', kwargs={'pk': restaurante.pk}))
    else:
        form = RestauranteForm(instance=restaurante)
    return render(request, 'restaurante/restaurante_edit.html', {'form': form, 'restaurante': restaurante})

@login_required
def excluir_restaurante(request, pk):
    # Apenas Admin pode excluir restaurantes.
    if request.user.role != 'admin':
        raise PermissionDenied("Você não tem permissão para excluir restaurantes.")
    
    restaurante = get_object_or_404(Restaurante, pk=pk)
    if request.method == 'POST':
        restaurante.delete()
        return redirect(reverse('restaurante:lista_restaurantes'))
    return redirect(reverse('restaurante:lista_restaurantes'))

@login_required
def visualizacao_dashboard(request, pk):
    restaurante = get_object_or_404(Restaurante, pk=pk)
    
    # Se o usuário for standard ou master, só pode acessar seu próprio restaurante.
    if request.user.role in ['standard', 'master'] and restaurante.id != request.user.restaurante.id:
        raise PermissionDenied("Você não tem permissão para acessar este restaurante.")
    
    try:
        receitas = restaurante.receitas.all()
    except AttributeError:
        receitas = []
    try:
        fichas = restaurante.fichas_tecnicas.all()
    except AttributeError:
        fichas = []
    
    receitas_data = [
        {
            'id': r.id,
            'nome_receita': getattr(r, 'nome_receita', str(r)),
            'preco_kg': float(r.preco_kg) if r.preco_kg is not None else 0,
        }
        for r in receitas
    ]
    fichas_data = [
        {
            'id': f.id,
            'descricao': f.descricao or "",
            'custo_total': float(f.custo_total) if f.custo_total is not None else 0,
        }
        for f in fichas
    ]
    context = {
        'restaurante': restaurante,
        'receitas': receitas,
        'fichas': fichas,
        'receitas_json': json.dumps(receitas_data),
        'fichas_json': json.dumps(fichas_data),
    }
    return render(request, 'restaurante/visualizacao_dashboard.html', context)
