import json
from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import inlineformset_factory
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required

from .models import Receita, ReceitaInsumo
from .forms import ReceitaForm, ReceitaInsumoForm
from restaurante.models import Restaurante
from insumos.models import Insumo

@login_required
def receita_cadastro(request, restaurante_id):
    # Apenas Admin pode criar receitas.
    if request.user.role in ['standard', 'master']:
        raise PermissionDenied("Você não tem permissão para criar receitas.")
    
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
            
            total_peso = Decimal("0.00")   # Em KG
            total_custo = Decimal("0.00")
            
            for item_form in formset_insumos:
                if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                    receita_insumo = item_form.save(commit=False)
                    receita_insumo.receita = receita
                    # Salva a unidade utilizada (pode ser alterada no form)
                    unit_used = item_form.cleaned_data.get('unidade', receita_insumo.insumo.unidade_medida)
                    receita_insumo.unit_used = unit_used
                    receita_insumo.save()
                    
                    # Normaliza a unidade para conversão (remove espaços e deixa em minúsculas)
                    insumo_unit = receita_insumo.insumo.unidade_medida.lower().strip()
                    quantidade = receita_insumo.quantidade_utilizada  # Valor informado
                    
                    # Se o insumo é cadastrado como "kg" ou "g", a quantidade informada é em gramas.
                    # Então, convertemos para kg dividindo por 1000.
                    if insumo_unit in ['kg', 'g']:
                        raw_weight = quantidade / Decimal("1000")
                    else:
                        raw_weight = quantidade
                        
                    # Se houver ajustes (opcional)
                    ajuste_tipo = item_form.cleaned_data.get('ajuste_tipo')
                    ajuste_sinal = item_form.cleaned_data.get('ajuste_sinal') or 'mais'
                    ajuste_percentual = item_form.cleaned_data.get('ajuste_percentual') or Decimal("0")
                    
                    if ajuste_tipo == 'ipc' and ajuste_percentual > 0:
                        effective_weight = raw_weight * (ajuste_percentual / Decimal("100"))
                    elif ajuste_tipo == 'fc' and ajuste_percentual > 0:
                        if ajuste_sinal == 'mais':
                            effective_weight = raw_weight * (1 - ajuste_percentual / Decimal("100"))
                        else:
                            effective_weight = raw_weight * (1 + ajuste_percentual / Decimal("100"))
                    else:
                        effective_weight = raw_weight
                        
                    total_peso += effective_weight
                    
                    # --- Ajuste no preço do insumo ---
                    # Caso o preço lido esteja com escala errada (por exemplo, 10000 em vez de 10),
                    # fazemos um ajuste dividindo por 1000.
                    insumo_preco = receita_insumo.insumo.preco
                    if insumo_preco > Decimal("100"):
                        insumo_preco = insumo_preco / Decimal("1000")
                    # --------------------------------------
                    
                    # Custo = peso efetivo (em kg) × preço do insumo (por kg)
                    computed_cost = effective_weight * insumo_preco
                    receita_insumo.custo_utilizado = computed_cost
                    receita_insumo.save()
                    
                    total_custo += computed_cost
            receita.peso_total = total_peso.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            receita.custo_total = total_custo.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            # Preço do KG = custo_total / peso_total (peso_total já está em kg)
            if total_peso > 0:
                receita.preco_kg = (total_custo / total_peso).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            receita.save()
            messages.success(request, "Receita cadastrada com sucesso.")
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

@login_required
def excluir_receita(request, pk):
    # Apenas Admin pode excluir receitas.
    if request.user.role in ['standard', 'master']:
        raise PermissionDenied("Você não tem permissão para excluir receitas.")
    receita = get_object_or_404(Receita, pk=pk)
    restaurante_id = receita.restaurante.id
    receita.delete()
    return redirect('restaurante:restaurante_detail', pk=restaurante_id)

@login_required
def detalhe_receita(request, receita_id):
    receita = get_object_or_404(Receita, pk=receita_id)
    
    # Apenas admin e master podem visualizar os preços
    show_prices = request.user.role in ['admin', 'master']
    
    # Valor de venda sugerido usando o fator de correção, se existir
    fator = receita.restaurante.fator_correcao_financeiro if hasattr(receita.restaurante, 'fator_correcao_financeiro') else Decimal("1.00")
    valor_venda_sugerida = receita.custo_total * fator if receita.custo_total is not None else None

    # Define calc_unit como "g" para exibir as quantidades em gramas
    context = {
        'receita': receita,
        'valor_venda_sugerida': valor_venda_sugerida,
        'show_prices': show_prices,
        'calc_unit': 'g',
    }
    return render(request, 'receitas/detalhe_receita.html', context)

@login_required
def api_detalhe_receita(request, receita_id):
    receita = get_object_or_404(Receita, pk=receita_id)
    fator = receita.restaurante.fator_correcao_financeiro if hasattr(receita.restaurante, 'fator_correcao_financeiro') else Decimal("1.00")
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
@login_required
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

@login_required
def editar_receita(request, receita_id):
    # Apenas Admin pode editar receitas.
    if request.user.role in ['standard', 'master']:
        raise PermissionDenied("Você não tem permissão para editar receitas.")
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
                    unit_used = item_form.cleaned_data.get('unidade', receita_insumo.insumo.unidade_medida)
                    receita_insumo.unit_used = unit_used
                    receita_insumo.save()
                    
                    # Normaliza a unidade para conversão
                    insumo_unit = receita_insumo.insumo.unidade_medida.lower().strip()
                    quantidade = receita_insumo.quantidade_utilizada
                    # Se o insumo é cadastrado como "kg" ou "g", converte a quantidade (informada em gramas) para kg
                    if insumo_unit in ['kg', 'g']:
                        raw_weight = quantidade / Decimal("1000")
                    else:
                        raw_weight = quantidade
                        
                    ajuste_tipo = item_form.cleaned_data.get('ajuste_tipo')
                    ajuste_sinal = item_form.cleaned_data.get('ajuste_sinal') or 'mais'
                    ajuste_percentual = item_form.cleaned_data.get('ajuste_percentual') or Decimal("0")
                    
                    if ajuste_tipo == 'ipc' and ajuste_percentual > 0:
                        effective_weight = raw_weight * (ajuste_percentual / Decimal("100"))
                    elif ajuste_tipo == 'fc' and ajuste_percentual > 0:
                        if ajuste_sinal == 'mais':
                            effective_weight = raw_weight * (1 - ajuste_percentual / Decimal("100"))
                        else:
                            effective_weight = raw_weight * (1 + ajuste_percentual / Decimal("100"))
                    else:
                        effective_weight = raw_weight
                    total_peso += effective_weight
                    
                    # --- Ajuste no preço do insumo ---
                    insumo_preco = receita_insumo.insumo.preco
                    if insumo_preco > Decimal("100"):
                        insumo_preco = insumo_preco / Decimal("1000")
                    # --------------------------------------
                    
                    # Aqui usamos o custo já armazenado (anteriormente calculado)
                    total_custo += receita_insumo.custo_utilizado
            receita.peso_total = total_peso.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            receita.custo_total = total_custo.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            if total_peso > 0:
                receita.preco_kg = (total_custo / total_peso).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            receita.save()
            messages.success(request, "Receita atualizada com sucesso.")
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
