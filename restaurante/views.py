from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Restaurante
from .forms import RestauranteForm, FatorCorrecaoForm

def cadastro_restaurante(request):
    if request.method == 'POST':
        form = RestauranteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('restaurante:lista_restaurantes'))
        else:
            # Para ajudar no debug, os erros serão exibidos no template
            print("Erros do formulário:", form.errors)
    else:
        form = RestauranteForm()
    return render(request, 'restaurante/cadastro_restaurante.html', {'form': form})

def lista_restaurantes(request):
    restaurantes = Restaurante.objects.all()
    return render(request, "restaurante/lista_restaurantes.html", {"restaurantes": restaurantes})

def restaurante_detail(request, pk):
    restaurante = get_object_or_404(Restaurante, pk=pk)
    # Supondo que a relação para receitas e insumos esteja configurada com related_name
    receitas = restaurante.receitas.all() if hasattr(restaurante, 'receitas') else []
    insumos = restaurante.insumos.all() if hasattr(restaurante, 'insumos') else []

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
        'fator_form': fator_form,
    }
    return render(request, 'restaurante/restaurante_detail.html', context)

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

def excluir_restaurante(request, pk):
    restaurante = get_object_or_404(Restaurante, pk=pk)
    if request.method == 'POST':
        restaurante.delete()
        return redirect(reverse('restaurante:lista_restaurantes'))
    return redirect(reverse('restaurante:lista_restaurantes'))
