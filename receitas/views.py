import json
from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import inlineformset_factory
from .models import Receita, ReceitaInsumo
from .forms import ReceitaForm, ReceitaInsumoForm
from restaurante.models import Restaurante
from insumos.models import Insumo

def receita_cadastro(request, restaurante_id):
    restaurante = get_object_or_404(Restaurante, pk=restaurante_id)
    ReceitaInsumoFormSet = inlineformset_factory(Receita, ReceitaInsumo, form=ReceitaInsumoForm, extra=1, can_delete=True)
    
    # Atualize o JSON para enviar as chaves 'unidade_medida' e 'peso'
    insumos = Insumo.objects.all()
    insumos_json = json.dumps([
        {
            'id': insumo.id,
            'preco': str(insumo.preco),
            'unidade_medida': insumo.unidade_medida,  # Por exemplo, "g"
            'peso': str(insumo.peso) if insumo.peso is not None else ""  # Peso base, ex.: "200.00"
        }
        for insumo in insumos
    ])
    
    if request.method == 'POST':
        form = ReceitaForm(request.POST, request.FILES)
        formset = ReceitaInsumoFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            receita = form.save(commit=False)
            receita.restaurante = restaurante
            receita.peso_total = Decimal("0.00")
            receita.custo_total = Decimal("0.00")
            receita.preco_kg = Decimal("0.00")
            receita.save()
            total_peso = Decimal("0.00")
            total_custo = Decimal("0.00")
            for item_form in formset:
                if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                    receita_insumo = item_form.save(commit=False)
                    receita_insumo.receita = receita
                    receita_insumo.save()
                    # Converte para gramas se o insumo estiver em kg; caso contrário, assume a quantidade já em g.
                    if receita_insumo.insumo.unidade_medida.lower() == 'kg':
                        total_peso += receita_insumo.quantidade_utilizada * Decimal("1000")
                    else:
                        total_peso += receita_insumo.quantidade_utilizada
                    if receita_insumo.custo_utilizado:
                        total_custo += receita_insumo.custo_utilizado
            receita.peso_total = total_peso.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            receita.custo_total = total_custo.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            if receita.peso_total and receita.peso_total > 0:
                receita.preco_kg = ((receita.custo_total / receita.peso_total) * Decimal("1000")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            receita.save()
            return redirect('restaurante:restaurante_detail', pk=restaurante.id)
    else:
        form = ReceitaForm()
        formset = ReceitaInsumoFormSet()
    
    return render(request, 'receitas/receita_cadastro.html', {
        'form': form,
        'formset': formset,
        'restaurante': restaurante,
        'insumos_json': insumos_json,
    })

def excluir_receita(request, pk):
    receita = get_object_or_404(Receita, pk=pk)
    restaurante_id = receita.restaurante.id
    receita.delete()
    return redirect('restaurante:restaurante_detail', pk=restaurante_id)
