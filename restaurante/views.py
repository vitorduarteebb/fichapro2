import json
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Restaurante
from .forms import RestauranteForm, FatorCorrecaoForm

# View para cadastro de restaurante (já existente)
def cadastro_restaurante(request):
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

# View para listar restaurantes (já existente)
def lista_restaurantes(request):
    restaurantes = Restaurante.objects.all()
    return render(request, "restaurante/lista_restaurantes.html", {"restaurantes": restaurantes})

# View para detalhes do restaurante com atualização inline do fator de correção
def restaurante_detail(request, pk):
    restaurante = get_object_or_404(Restaurante, pk=pk)
    receitas = restaurante.receitas.all()  # Supondo que o related_name em Receita seja 'receitas'
    insumos = restaurante.insumos.all()    # Supondo que o related_name em Insumo seja 'insumos'
    # Aqui assumimos que o modelo FichaTecnica possui:
    #    restaurante = models.ForeignKey(Restaurante, on_delete=models.CASCADE, related_name='fichas_tecnicas')
    fichas_tecnicas = restaurante.fichas_tecnicas.all()  # Query para obter as fichas técnicas associadas

    # Tratamento do formulário inline para atualizar o fator de correção
    if request.method == 'POST':
        fator_form = FatorCorrecaoForm(request.POST, instance=restaurante)
        if fator_form.is_valid():
            fator_form.save()
            return redirect(reverse('restaurante:restaurante_detail', kwargs={'pk': restaurante.pk}))
    else:
        fator_form = FatorCorrecaoForm(instance=restaurante)

    context = {
        'restaurante': restaurante,
        'receitas': receitas,
        'insumos': insumos,
        'fichas_tecnicas': fichas_tecnicas,  # Variável adicionada para o template
        'fator_form': fator_form,
    }
    return render(request, 'restaurante/restaurante_detail.html', context)
# View para editar restaurante (já existente)
def restaurante_edit(request, pk):
    restaurante = get_object_or_404(Restaurante, pk=pk)
    if request.method == 'POST':
        form = RestauranteForm(request.POST, instance=restaurante)
        if form.is_valid():
            form.save()
            return redirect(reverse('restaurante:restaurante_detail', kwargs={'pk': restaurante.pk}))
    else:
        form = RestauranteForm(instance=restaurante)
    return render(request, 'restaurante/restaurante_edit.html', {'form': form, 'restaurante': restaurante})

# View para excluir restaurante (já existente)
def excluir_restaurante(request, pk):
    restaurante = get_object_or_404(Restaurante, pk=pk)
    if request.method == 'POST':
        restaurante.delete()
        return redirect(reverse('restaurante:lista_restaurantes'))
    return redirect(reverse('restaurante:lista_restaurantes'))

# Nova view: Dashboard (Visualização dinâmica)
def visualizacao_dashboard(request, pk):
    """
    Exibe um dashboard dinâmico com informações de receitas e fichas técnicas do restaurante.
    Os custos são recalculados com base no valor do fator de correção.
    """
    restaurante = get_object_or_404(Restaurante, pk=pk)
    
    # Obtenha receitas e fichas técnicas associados ao restaurante.
    try:
        receitas = restaurante.receitas.all()
    except AttributeError:
        receitas = []
    try:
        # Aqui, assumindo que o related_name para fichas técnicas seja 'fichas_tecnicas'
        fichas = restaurante.fichas_tecnicas.all()
    except AttributeError:
        fichas = []
    
    # Preparar dados para uso via JSON (opcional, para funcionalidades avançadas)
    receitas_data = [
        {
            'id': r.id,
            'nome_receita': getattr(r, 'nome_receita', str(r)),
            'preco_kg': float(r.preco_kg) if hasattr(r, 'preco_kg') and r.preco_kg is not None else 0,
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
