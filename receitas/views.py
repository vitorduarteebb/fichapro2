import json
from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import inlineformset_factory
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Receita, ReceitaInsumo
from .forms import ReceitaForm, ReceitaInsumoForm
from restaurante.models import Restaurante
from insumos.models import Insumo

def receita_cadastro(request, restaurante_id):
    restaurante = get_object_or_404(Restaurante, pk=restaurante_id)
    ReceitaInsumoFormSet = inlineformset_factory(
        Receita, ReceitaInsumo, form=ReceitaInsumoForm, extra=1, can_delete=True
    )
    
    insumos = Insumo.objects.all()
    insumos_json = json.dumps([
        {
            'id': insumo.id,
            'preco': str(insumo.preco),
            'unidade': insumo.unidade_medida,
            'quantidade': str(insumo.quantidade)
        }
        for insumo in insumos
    ])
    
    if request.method == 'POST':
        form = ReceitaForm(request.POST, request.FILES)
        formset_insumos = ReceitaInsumoFormSet(request.POST, prefix='insumos')
        if form.is_valid() and formset_insumos.is_valid():
            receita = form.save(commit=False)
            receita.restaurante = restaurante
            receita.peso_total = Decimal("0.00")
            receita.custo_total = Decimal("0.00")
            receita.preco_kg = Decimal("0.00")
            receita.save()
            
            total_peso = Decimal("0.00")
            total_custo = Decimal("0.00")
            
            for item_form in formset_insumos:
                if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                    receita_insumo = item_form.save(commit=False)
                    receita_insumo.receita = receita
                    # Guarda a unidade usada (campo transitório)
                    unit_used = item_form.cleaned_data.get('unidade', receita_insumo.insumo.unidade_medida)
                    receita_insumo.unit_used = unit_used
                    receita_insumo.save()
                    
                    # Converte a quantidade para gramas
                    insumo_unit = receita_insumo.insumo.unidade_medida.lower()
                    quantidade = receita_insumo.quantidade_utilizada
                    if insumo_unit == 'kg':
                        raw_weight = quantidade * Decimal("1000")
                    elif insumo_unit == 'g':
                        raw_weight = quantidade
                    else:
                        raw_weight = quantidade
                        
                    ajuste_tipo = item_form.cleaned_data.get('ajuste_tipo')
                    ajuste_sinal = item_form.cleaned_data.get('ajuste_sinal') or 'mais'
                    ajuste_percentual = item_form.cleaned_data.get('ajuste_percentual') or Decimal("0")
                    
                    if ajuste_tipo == 'ipc' and ajuste_percentual > 0:
                        effective_weight = raw_weight * (ajuste_percentual / Decimal("100"))
                    elif ajuste_tipo == 'fc' and ajuste_percentual > 0:
                        if ajuste_sinal == 'mais':
                            effective_weight = raw_weight * (1 + ajuste_percentual / Decimal("100"))
                        else:
                            effective_weight = raw_weight * (1 - ajuste_percentual / Decimal("100"))
                    else:
                        effective_weight = raw_weight
                        
                    total_peso += effective_weight
                    total_custo += receita_insumo.custo_utilizado
            receita.peso_total = total_peso.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            receita.custo_total = total_custo.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            if total_peso > 0:
                receita.preco_kg = (total_custo / (total_peso / Decimal("1000"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            receita.save()
            return redirect('restaurante:restaurante_detail', pk=restaurante.id)
    else:
        form = ReceitaForm()
        formset_insumos = ReceitaInsumoFormSet(prefix='insumos')
    
    return render(request, 'receitas/receita_cadastro.html', {
        'form': form,
        'formset_insumos': formset_insumos,
        'restaurante': restaurante,
        'insumos_json': insumos_json,
    })

def excluir_receita(request, pk):
    receita = get_object_or_404(Receita, pk=pk)
    restaurante_id = receita.restaurante.id
    receita.delete()
    return redirect('restaurante:restaurante_detail', pk=restaurante_id)

def detalhe_receita(request, receita_id):
    receita = get_object_or_404(Receita, pk=receita_id)
    fator = (receita.restaurante.fator_correcao_financeiro
             if hasattr(receita.restaurante, 'fator_correcao_financeiro')
             else Decimal("1.00"))
    valor_venda_sugerida = receita.custo_total * fator if receita.custo_total is not None else None
    return render(request, 'receitas/detalhe_receita.html', {
        'receita': receita,
        'valor_venda_sugerida': valor_venda_sugerida,
    })

def api_detalhe_receita(request, receita_id):
    receita = get_object_or_404(Receita, pk=receita_id)
    fator = (receita.restaurante.fator_correcao_financeiro
             if hasattr(receita.restaurante, 'fator_correcao_financeiro')
             else Decimal("1.00"))
    valor_venda_sugerida = receita.custo_total * fator if receita.custo_total is not None else ""
    data = {
        'porcao_sugerida': str(receita.porcao_sugerida),
        'tempo_preparo': receita.tempo_preparo,
        'preco_kg': str(receita.preco_kg),
        'rendimento': receita.rendimento() if receita.rendimento() else "",
        'valor_venda_sugerida': str(valor_venda_sugerida),
    }
    return JsonResponse(data)

@require_POST
def atualizar_valor_trabalhado(request, receita_id):
    receita = get_object_or_404(Receita, pk=receita_id)
    novo_valor = request.POST.get('valor_trabalhado')
    try:
        novo_valor_decimal = Decimal(novo_valor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except Exception:
        messages.error(request, "VALOR INVÁLIDO.")
        return redirect('receitas:detalhe_receita', receita_id=receita.id)
    receita.valor_trabalhado = novo_valor_decimal
    receita.save()
    messages.success(request, "VALOR TRABALHADO ATUALIZADO COM SUCESSO.")
    return redirect('receitas:detalhe_receita', receita_id=receita.id)

def editar_receita(request, receita_id):
    receita = get_object_or_404(Receita, pk=receita_id)
    restaurante = receita.restaurante
    ReceitaInsumoFormSet = inlineformset_factory(
        Receita, ReceitaInsumo, form=ReceitaInsumoForm, extra=1, can_delete=True
    )
    
    if request.method == 'POST':
        form = ReceitaForm(request.POST, request.FILES, instance=receita)
        formset_insumos = ReceitaInsumoFormSet(request.POST, instance=receita, prefix='insumos')
        if form.is_valid() and formset_insumos.is_valid():
            receita = form.save(commit=False)
            # Reinicia os totais para recalcular
            receita.peso_total = Decimal("0.00")
            receita.custo_total = Decimal("0.00")
            receita.preco_kg = Decimal("0.00")
            receita.save()
            total_peso = Decimal("0.00")
            total_custo = Decimal("0.00")
            
            # Processa os formulários que não estão marcados para deleção
            for item_form in formset_insumos:
                if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                    receita_insumo = item_form.save(commit=False)
                    receita_insumo.receita = receita
                    unit_used = item_form.cleaned_data.get('unidade', receita_insumo.insumo.unidade_medida)
                    receita_insumo.unit_used = unit_used
                    receita_insumo.save()
                    
                    insumo_unit = receita_insumo.insumo.unidade_medida.lower()
                    quantidade = receita_insumo.quantidade_utilizada
                    if insumo_unit == 'kg':
                        raw_weight = quantidade * Decimal("1000")
                    elif insumo_unit == 'g':
                        raw_weight = quantidade
                    else:
                        raw_weight = quantidade
                        
                    ajuste_tipo = item_form.cleaned_data.get('ajuste_tipo')
                    ajuste_sinal = item_form.cleaned_data.get('ajuste_sinal') or 'mais'
                    ajuste_percentual = item_form.cleaned_data.get('ajuste_percentual') or Decimal("0")
                    
                    if ajuste_tipo == 'ipc' and ajuste_percentual > 0:
                        effective_weight = raw_weight * (ajuste_percentual / Decimal("100"))
                    elif ajuste_tipo == 'fc' and ajuste_percentual > 0:
                        if ajuste_sinal == 'mais':
                            effective_weight = raw_weight * (1 + ajuste_percentual/Decimal("100"))
                        else:
                            effective_weight = raw_weight * (1 - ajuste_percentual/Decimal("100"))
                    else:
                        effective_weight = raw_weight
                    total_peso += effective_weight
                    total_custo += receita_insumo.custo_utilizado
            
            # Trata as deleções (itens marcados para DELETE)
            for item_form in formset_insumos.deleted_forms:
                if item_form.instance.pk:
                    item_form.instance.delete()
            
            receita.peso_total = total_peso.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            receita.custo_total = total_custo.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            if total_peso > 0:
                receita.preco_kg = (total_custo / (total_peso / Decimal("1000"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            receita.save()
            messages.success(request, "RECEITA ATUALIZADA COM SUCESSO.")
            return redirect('receitas:detalhe_receita', receita_id=receita.id)
    else:
        form = ReceitaForm(instance=receita)
        formset_insumos = ReceitaInsumoFormSet(instance=receita, prefix='insumos')
    
    insumos = Insumo.objects.all()
    insumos_json = json.dumps([
        {
            'id': insumo.id,
            'preco': str(insumo.preco),
            'unidade': insumo.unidade_medida,
            'quantidade': str(insumo.quantidade)
        }
        for insumo in insumos
    ])
    
    return render(request, 'receitas/editar_receita.html', {
        'form': form,
        'formset_insumos': formset_insumos,
        'receita': receita,
        'insumos_json': insumos_json,
    })
