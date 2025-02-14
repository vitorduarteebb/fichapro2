import json
from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import inlineformset_factory
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import FichaTecnica, FichaTecnicaInsumo, FichaTecnicaReceita
from .forms import FichaTecnicaForm, FichaTecnicaInsumoForm, FichaTecnicaReceitaForm
from restaurante.models import Restaurante
from insumos.models import Insumo
from receitas.models import Receita

def editar_ficha_tecnica(request, ficha_id):
    ficha = get_object_or_404(FichaTecnica, pk=ficha_id)
    restaurante = ficha.restaurante
    # Cria os formsets vinculados à instância existente
    FichaTecnicaInsumoFormSet = inlineformset_factory(
        FichaTecnica, FichaTecnicaInsumo, form=FichaTecnicaInsumoForm, extra=1, can_delete=True
    )
    FichaTecnicaReceitaFormSet = inlineformset_factory(
        FichaTecnica, FichaTecnicaReceita, form=FichaTecnicaReceitaForm, extra=1, can_delete=True
    )

    if request.method == 'POST':
        form = FichaTecnicaForm(request.POST, request.FILES, instance=ficha)
        formset_insumos = FichaTecnicaInsumoFormSet(request.POST, instance=ficha, prefix='insumos')
        formset_receitas = FichaTecnicaReceitaFormSet(request.POST, instance=ficha, prefix='receitas')
        if form.is_valid() and formset_insumos.is_valid() and formset_receitas.is_valid():
            ficha = form.save(commit=False)
            # Reinicia os totais para recalcular
            ficha.peso_total = Decimal("0.00")
            ficha.custo_total_insumos = Decimal("0.00")
            ficha.custo_total_receitas = Decimal("0.00")
            ficha.valor_venda_sugerida = Decimal("0.00")
            ficha.save()
            
            total_peso = Decimal("0.00")
            total_custo_insumos = Decimal("0.00")
            for item_form in formset_insumos:
                if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                    ficha_insumo = item_form.save(commit=False)
                    ficha_insumo.ficha_tecnica = ficha
                    ficha_insumo.save()
                    insumo_unit = ficha_insumo.insumo.unidade_medida.lower()
                    quantidade = ficha_insumo.quantidade_utilizada
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
                    elif ajuste_tipo == 'fator' and ajuste_percentual > 0:
                        if ajuste_sinal == 'mais':
                            effective_weight = raw_weight * (1 + ajuste_percentual / Decimal("100"))
                        else:
                            effective_weight = raw_weight * (1 - ajuste_percentual / Decimal("100"))
                    else:
                        effective_weight = raw_weight
                    total_peso += effective_weight
                    if ficha_insumo.custo_utilizado:
                        total_custo_insumos += ficha_insumo.custo_utilizado
            total_custo_receitas = Decimal("0.00")
            for item_form in formset_receitas:
                if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                    ficha_receita = item_form.save(commit=False)
                    ficha_receita.ficha_tecnica = ficha
                    ficha_receita.save()
                    if ficha_receita.custo_utilizado:
                        total_custo_receitas += ficha_receita.custo_utilizado
                    if ficha_receita.receita.porcao_sugerida and ficha_receita.receita.peso_total:
                        porcao = ficha_receita.receita.porcao_sugerida
                        peso_receita = ficha_receita.receita.peso_total
                        if ficha_receita.unidade.lower() == 'g':
                            used_quantity = ficha_receita.quantidade_utilizada
                        else:
                            used_quantity = ficha_receita.quantidade_utilizada * Decimal("1000")
                        effective_weight_recipe = (used_quantity / porcao) * peso_receita
                        total_peso += effective_weight_recipe
            ficha.peso_total = total_peso.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ficha.custo_total_insumos = total_custo_insumos.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ficha.custo_total_receitas = total_custo_receitas.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ficha.valor_venda_sugerida = ((ficha.custo_total_insumos + ficha.custo_total_receitas) * restaurante.fator_correcao_financeiro).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ficha.save()
            messages.success(request, "Ficha Técnica atualizada com sucesso.")
            return redirect('fichas_tecnicas:detalhe_ficha', ficha_id=ficha.id)
    else:
        form = FichaTecnicaForm(instance=ficha)
        formset_insumos = FichaTecnicaInsumoFormSet(instance=ficha, prefix='insumos')
        formset_receitas = FichaTecnicaReceitaFormSet(instance=ficha, prefix='receitas')
    
    # Prepara os dados em JSON para o JavaScript (mesmos dados de insumos e receitas)
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
    receitas = Receita.objects.all()
    receitas_json = json.dumps([
        {
            'id': receita.id,
            'preco_kg': str(receita.preco_kg if receita.preco_kg is not None else "0.00"),
            'porcao_sugerida': str(receita.porcao_sugerida),
            'peso_total': str(receita.peso_total if receita.peso_total is not None else "0.00")
        }
        for receita in receitas
    ])
    
    return render(request, 'fichas_tecnicas/editar_ficha_tecnica.html', {
        'form': form,
        'formset_insumos': formset_insumos,
        'formset_receitas': formset_receitas,
        'restaurante': restaurante,
        'insumos_json': insumos_json,
        'receitas_json': receitas_json,
        'ficha': ficha,
    })

def ficha_tecnica_cadastro(request, restaurante_id):
    restaurante = get_object_or_404(Restaurante, pk=restaurante_id)
    # Definindo os formsets com nomes consistentes
    FichaTecnicaInsumoFormSet = inlineformset_factory(
        FichaTecnica, FichaTecnicaInsumo, form=FichaTecnicaInsumoForm, extra=1, can_delete=True
    )
    FichaTecnicaReceitaFormSet = inlineformset_factory(
        FichaTecnica, FichaTecnicaReceita, form=FichaTecnicaReceitaForm, extra=1, can_delete=True
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
    receitas = Receita.objects.all()
    receitas_json = json.dumps([
        {
            'id': receita.id,
            'preco_kg': str(receita.preco_kg if receita.preco_kg is not None else "0.00"),
            'porcao_sugerida': str(receita.porcao_sugerida),
            'peso_total': str(receita.peso_total if receita.peso_total is not None else "0.00")
        }
        for receita in receitas
    ])
    
    if request.method == 'POST':
        form = FichaTecnicaForm(request.POST, request.FILES)
        formset_insumos = FichaTecnicaInsumoFormSet(request.POST, prefix='insumos')
        formset_receitas = FichaTecnicaReceitaFormSet(request.POST, prefix='receitas')
        if form.is_valid() and formset_insumos.is_valid() and formset_receitas.is_valid():
            ficha = form.save(commit=False)
            ficha.restaurante = restaurante
            ficha.peso_total = Decimal("0.00")
            ficha.custo_total_insumos = Decimal("0.00")
            ficha.custo_total_receitas = Decimal("0.00")
            ficha.valor_venda_sugerida = Decimal("0.00")
            ficha.save()
            
            total_peso = Decimal("0.00")
            total_custo_insumos = Decimal("0.00")
            for item_form in formset_insumos:
                if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                    ficha_insumo = item_form.save(commit=False)
                    ficha_insumo.ficha_tecnica = ficha
                    ficha_insumo.save()
                    insumo_unit = ficha_insumo.insumo.unidade_medida.lower()
                    quantidade = ficha_insumo.quantidade_utilizada
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
                    elif ajuste_tipo == 'fator' and ajuste_percentual > 0:
                        if ajuste_sinal == 'mais':
                            effective_weight = raw_weight * (1 + ajuste_percentual / Decimal("100"))
                        else:
                            effective_weight = raw_weight * (1 - ajuste_percentual / Decimal("100"))
                    else:
                        effective_weight = raw_weight
                    total_peso += effective_weight
                    if ficha_insumo.custo_utilizado:
                        total_custo_insumos += ficha_insumo.custo_utilizado
            
            total_custo_receitas = Decimal("0.00")
            for item_form in formset_receitas:
                if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                    ficha_receita = item_form.save(commit=False)
                    ficha_receita.ficha_tecnica = ficha
                    ficha_receita.save()
                    if ficha_receita.custo_utilizado:
                        total_custo_receitas += ficha_receita.custo_utilizado
                    if ficha_receita.receita.porcao_sugerida and ficha_receita.receita.peso_total:
                        porcao = ficha_receita.receita.porcao_sugerida
                        peso_receita = ficha_receita.receita.peso_total
                        if ficha_receita.unidade.lower() == 'g':
                            used_quantity = ficha_receita.quantidade_utilizada
                        else:
                            used_quantity = ficha_receita.quantidade_utilizada * Decimal("1000")
                        effective_weight_recipe = (used_quantity / porcao) * peso_receita
                        total_peso += effective_weight_recipe
            ficha.peso_total = total_peso.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ficha.custo_total_insumos = total_custo_insumos.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ficha.custo_total_receitas = total_custo_receitas.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ficha.valor_venda_sugerida = (
                (ficha.custo_total_insumos + ficha.custo_total_receitas) *
                restaurante.fator_correcao_financeiro
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ficha.save()
            return redirect('restaurante:restaurante_detail', pk=restaurante.id)
    else:
        form = FichaTecnicaForm()
        formset_insumos = FichaTecnicaInsumoFormSet(prefix='insumos')
        formset_receitas = FichaTecnicaReceitaFormSet(prefix='receitas')
    
    return render(request, 'fichas_tecnicas/ficha_tecnica_cadastro.html', {
        'form': form,
        'formset_insumos': formset_insumos,
        'formset_receitas': formset_receitas,
        'restaurante': restaurante,
        'insumos_json': insumos_json,
        'receitas_json': receitas_json,
    })

def excluir_ficha_tecnica(request, pk):
    ficha = get_object_or_404(FichaTecnica, pk=pk)
    restaurante_id = ficha.restaurante.id
    ficha.delete()
    return redirect('restaurante:restaurante_detail', pk=restaurante_id)

def detalhe_ficha_tecnica(request, ficha_id):
    ficha = get_object_or_404(FichaTecnica, pk=ficha_id)
    return render(request, 'fichas_tecnicas/detalhe_ficha_tecnica.html', {
        'ficha': ficha,
        'valor_venda_sugerida': ficha.valor_venda_sugerida,
    })

def api_detalhe_ficha(request, ficha_id):
    ficha = get_object_or_404(FichaTecnica, pk=ficha_id)
    data = {
        'porcao_sugerida': str(ficha.porcao_sugerida),
        'tempo_preparo': ficha.tempo_preparo,
        'valor_venda_sugerida': str(ficha.valor_venda_sugerida),
    }
    return JsonResponse(data)

@require_POST
def atualizar_valor_trabalhado(request, ficha_id):
    ficha = get_object_or_404(FichaTecnica, pk=ficha_id)
    novo_valor = request.POST.get('valor_trabalhado')
    try:
        novo_valor_decimal = Decimal(novo_valor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except Exception:
        messages.error(request, "VALOR INVÁLIDO.")
        return redirect('fichas_tecnicas:detalhe_ficha', ficha_id=ficha.id)
    ficha.valor_trabalhado = novo_valor_decimal
    ficha.save()
    messages.success(request, "VALOR TRABALHADO ATUALIZADO COM SUCESSO.")
    return redirect('fichas_tecnicas:detalhe_ficha', ficha_id=ficha.id)
