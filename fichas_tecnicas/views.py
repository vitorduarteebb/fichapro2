import json
from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.forms.models import inlineformset_factory  # Importação necessária

from .models import FichaTecnica, FichaTecnicaInsumo, FichaTecnicaReceita
from .forms import FichaTecnicaForm, FichaTecnicaInsumoForm, FichaTecnicaReceitaForm
from restaurante.models import Restaurante
from insumos.models import Insumo
from receitas.models import Receita

def ficha_tecnica_cadastro(request, restaurante_id):
    # Apenas Admin pode criar fichas técnicas.
    if request.user.role in ['standard', 'master']:
        raise PermissionDenied("Você não tem permissão para criar fichas técnicas.")
    restaurante = get_object_or_404(Restaurante, pk=restaurante_id)
    
    # Criação dos inline formsets
    FichaTecnicaInsumoFormSet = inlineformset_factory(
        FichaTecnica, FichaTecnicaInsumo, form=FichaTecnicaInsumoForm, extra=1, can_delete=True
    )
    FichaTecnicaReceitaFormSet = inlineformset_factory(
        FichaTecnica, FichaTecnicaReceita, form=FichaTecnicaReceitaForm, extra=1, can_delete=True
    )

    # Serializa dados para uso no frontend (JavaScript, se necessário)
    insumos = Insumo.objects.all()
    insumos_json = json.dumps([{
        'id': insumo.id,
        'preco': str(insumo.preco),
        'unidade': insumo.unidade_medida,
        'quantidade': str(insumo.quantidade)
    } for insumo in insumos])
    receitas = Receita.objects.all()
    receitas_json = json.dumps([{
        'id': receita.id,
        'preco_kg': str(receita.preco_kg if receita.preco_kg is not None else "0.00"),
        'porcao_sugerida': str(receita.porcao_sugerida),
        'peso_total': str(receita.peso_total if receita.peso_total is not None else "0.00")
    } for receita in receitas])
    
    # --- Parâmetro que indica a unidade de entrada (cálculo) ---
    # Se o usuário informar ?calc_unit=g na URL, entende-se que as quantidades são informadas em gramas.
    # Se for ?calc_unit=kg, as quantidades são em kg.
    calc_unit = request.GET.get('calc_unit', 'g').lower()

    if request.method == 'POST':
        form = FichaTecnicaForm(request.POST, request.FILES)
        formset_insumos = FichaTecnicaInsumoFormSet(request.POST, prefix='insumos')
        formset_receitas = FichaTecnicaReceitaFormSet(request.POST, prefix='receitas')
        if form.is_valid() and formset_insumos.is_valid() and formset_receitas.is_valid():
            ficha = form.save(commit=False)
            ficha.restaurante = restaurante
            # Inicializa os acumuladores
            total_peso_kg = Decimal("0.00")          # Peso total (para cálculo) em kg
            total_custo_insumos = Decimal("0.00")
            ficha.save()
            
            # Processamento dos insumos
            for item_form in formset_insumos:
                if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                    ficha_insumo = item_form.save(commit=False)
                    ficha_insumo.ficha_tecnica = ficha
                    # Obtemos a unidade cadastrada para o insumo ('kg' ou 'g')
                    insumo_unit = ficha_insumo.insumo.unidade_medida.lower()
                    quantidade = ficha_insumo.quantidade_utilizada  # Valor informado pelo usuário
                    
                    # Converter para kg para cálculo:
                    # Se o usuário informou valores em gramas (calc_unit == 'g'),
                    # converte dividindo por 1000; se em kg, usa o valor diretamente.
                    if calc_unit == 'g':
                        weight_in_kg = quantidade / Decimal("1000")
                    elif calc_unit == 'kg':
                        weight_in_kg = quantidade
                    else:
                        weight_in_kg = quantidade / Decimal("1000")
                    
                    # Aplica ajuste, se houver (mantendo a lógica original)
                    ajuste_tipo = item_form.cleaned_data.get('ajuste_tipo')
                    ajuste_sinal = item_form.cleaned_data.get('ajuste_sinal') or 'mais'
                    ajuste_percentual = item_form.cleaned_data.get('ajuste_percentual') or Decimal("0")
                    if ajuste_tipo == 'ipc' and ajuste_percentual > 0:
                        effective_weight = weight_in_kg * (ajuste_percentual / Decimal("100"))
                    elif ajuste_tipo == 'fc' and ajuste_percentual > 0:
                        effective_weight = weight_in_kg * (1 + ajuste_percentual / Decimal("100")) if ajuste_sinal == 'menos' else weight_in_kg * (1 - ajuste_percentual / Decimal("100"))
                    else:
                        effective_weight = weight_in_kg

                    # Custo: peso (em kg) × preço (por kg)
                    computed_cost = effective_weight * ficha_insumo.insumo.preco
                    ficha_insumo.custo_utilizado = computed_cost
                    ficha_insumo.save()
                    
                    total_peso_kg += effective_weight
                    total_custo_insumos += computed_cost
            
            total_custo_receitas = Decimal("0.00")
            # Processamento das receitas (conversões análogas)
            for item_form in formset_receitas:
                if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                    ficha_receita = item_form.save(commit=False)
                    ficha_receita.ficha_tecnica = ficha
                    ficha_receita.save()
                    if ficha_receita.custo_utilizado:
                        total_custo_receitas += ficha_receita.custo_utilizado
                    
                    if ficha_receita.receita.porcao_sugerida and ficha_receita.receita.peso_total:
                        porcao = Decimal(ficha_receita.receita.porcao_sugerida)   # em gramas
                        peso_receita = Decimal(ficha_receita.receita.peso_total)    # em gramas
                        # Conversão para receitas:
                        if calc_unit == 'g':
                            used_quantity_in_g = ficha_receita.quantidade_utilizada
                        elif calc_unit == 'kg':
                            used_quantity_in_g = ficha_receita.quantidade_utilizada * Decimal("1000")
                        else:
                            used_quantity_in_g = ficha_receita.quantidade_utilizada
                        
                        effective_weight_recipe_in_g = (used_quantity_in_g / porcao) * peso_receita
                        effective_weight_recipe_in_kg = effective_weight_recipe_in_g / Decimal("1000")
                        total_peso_kg += effective_weight_recipe_in_kg
                        custo_proporcional = effective_weight_recipe_in_kg * Decimal(ficha_receita.receita.preco_kg)
                        total_custo_receitas += custo_proporcional
            
            # Armazena o peso total na ficha técnica para exibição:
            # Se calc_unit for 'g', converte o total (em kg) para gramas; se 'kg', mantém em kg.
            if calc_unit == 'kg':
                ficha.peso_total = total_peso_kg.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            else:
                ficha.peso_total = (total_peso_kg * Decimal("1000")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            
            # Atualiza os campos de custos e o valor de venda
            ficha.custo_total_insumos = total_custo_insumos.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ficha.custo_total_receitas = total_custo_receitas.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ficha.valor_venda_sugerida = ((total_custo_insumos + total_custo_receitas) * restaurante.fator_correcao_financeiro).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ficha.save()
            messages.success(request, "Ficha Técnica cadastrada com sucesso.")
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

def editar_ficha_tecnica(request, ficha_id):
    ficha = get_object_or_404(FichaTecnica, pk=ficha_id)
    restaurante = ficha.restaurante
    if request.user.role in ['standard', 'master']:
        raise PermissionDenied("Você não tem permissão para editar fichas técnicas.")
    FichaTecnicaInsumoFormSet = inlineformset_factory(
        FichaTecnica, FichaTecnicaInsumo, form=FichaTecnicaInsumoForm, extra=1, can_delete=True
    )
    FichaTecnicaReceitaFormSet = inlineformset_factory(
        FichaTecnica, FichaTecnicaReceita, form=FichaTecnicaReceitaForm, extra=1, can_delete=True
    )
    
    calc_unit = request.GET.get('calc_unit', 'g').lower()
    
    if request.method == 'POST':
        form = FichaTecnicaForm(request.POST, request.FILES, instance=ficha)
        formset_insumos = FichaTecnicaInsumoFormSet(request.POST, instance=ficha, prefix='insumos')
        formset_receitas = FichaTecnicaReceitaFormSet(request.POST, instance=ficha, prefix='receitas')
        if form.is_valid() and formset_insumos.is_valid() and formset_receitas.is_valid():
            ficha = form.save(commit=False)
            total_peso_kg = Decimal("0.00")
            total_custo_insumos = Decimal("0.00")
            ficha.save()
            
            for item_form in formset_insumos:
                if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                    ficha_insumo = item_form.save(commit=False)
                    ficha_insumo.ficha_tecnica = ficha
                    insumo_unit = ficha_insumo.insumo.unidade_medida.lower()
                    quantidade = ficha_insumo.quantidade_utilizada
                    if calc_unit == 'g':
                        weight_in_kg = quantidade / Decimal("1000")
                    elif calc_unit == 'kg':
                        weight_in_kg = quantidade
                    else:
                        weight_in_kg = quantidade / Decimal("1000")
                    
                    ajuste_tipo = item_form.cleaned_data.get('ajuste_tipo')
                    ajuste_sinal = item_form.cleaned_data.get('ajuste_sinal') or 'mais'
                    ajuste_percentual = item_form.cleaned_data.get('ajuste_percentual') or Decimal("0")
                    if ajuste_tipo == 'ipc' and ajuste_percentual > 0:
                        effective_weight = weight_in_kg * (ajuste_percentual / Decimal("100"))
                    elif ajuste_tipo == 'fc' and ajuste_percentual > 0:
                        effective_weight = weight_in_kg * (1 + ajuste_percentual / Decimal("100")) if ajuste_sinal == 'menos' else weight_in_kg * (1 - ajuste_percentual / Decimal("100"))
                    else:
                        effective_weight = weight_in_kg
                    
                    computed_cost = effective_weight * ficha_insumo.insumo.preco
                    ficha_insumo.custo_utilizado = computed_cost
                    ficha_insumo.save()
                    total_peso_kg += effective_weight
                    total_custo_insumos += computed_cost
            
            total_custo_receitas = Decimal("0.00")
            for item_form in formset_receitas:
                if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                    ficha_receita = item_form.save(commit=False)
                    ficha_receita.ficha_tecnica = ficha
                    ficha_receita.save()
                    if ficha_receita.custo_utilizado:
                        total_custo_receitas += ficha_receita.custo_utilizado
                    if ficha_receita.receita.porcao_sugerida and ficha_receita.receita.peso_total:
                        porcao = Decimal(ficha_receita.receita.porcao_sugerida)
                        peso_receita = Decimal(ficha_receita.receita.peso_total)
                        if calc_unit == 'g':
                            used_quantity_in_g = ficha_receita.quantidade_utilizada
                        elif calc_unit == 'kg':
                            used_quantity_in_g = ficha_receita.quantidade_utilizada * Decimal("1000")
                        else:
                            used_quantity_in_g = ficha_receita.quantidade_utilizada
                        
                        effective_weight_recipe_in_g = (used_quantity_in_g / porcao) * peso_receita
                        effective_weight_recipe_in_kg = effective_weight_recipe_in_g / Decimal("1000")
                        total_peso_kg += effective_weight_recipe_in_kg
                        custo_proporcional = effective_weight_recipe_in_kg * Decimal(ficha_receita.receita.preco_kg)
                        total_custo_receitas += custo_proporcional
            if calc_unit == 'kg':
                ficha.peso_total = total_peso_kg.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            else:
                ficha.peso_total = (total_peso_kg * Decimal("1000")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ficha.custo_total_insumos = total_custo_insumos.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ficha.custo_total_receitas = total_custo_receitas.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ficha.valor_venda_sugerida = ((total_custo_insumos + total_custo_receitas) * restaurante.fator_correcao_financeiro).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ficha.save()
            messages.success(request, "Ficha Técnica atualizada com sucesso.")
            return redirect('fichas_tecnicas:detalhe_ficha', ficha_id=ficha.id)
    else:
        form = FichaTecnicaForm(instance=ficha)
        formset_insumos = FichaTecnicaInsumoFormSet(instance=ficha, prefix='insumos')
        formset_receitas = FichaTecnicaReceitaFormSet(instance=ficha, prefix='receitas')
    
    insumos = Insumo.objects.all()
    insumos_json = json.dumps([{
        'id': insumo.id,
        'preco': str(insumo.preco),
        'unidade': insumo.unidade_medida,
        'quantidade': str(insumo.quantidade)
    } for insumo in insumos])
    receitas = Receita.objects.all()
    receitas_json = json.dumps([{
        'id': receita.id,
        'preco_kg': str(receita.preco_kg if receita.preco_kg is not None else "0.00"),
        'porcao_sugerida': str(receita.porcao_sugerida),
        'peso_total': str(receita.peso_total if receita.peso_total is not None else "0.00")
    } for receita in receitas])
    
    return render(request, 'fichas_tecnicas/editar_ficha_tecnica.html', {
        'form': form,
        'formset_insumos': formset_insumos,
        'formset_receitas': formset_receitas,
        'restaurante': restaurante,
        'insumos_json': insumos_json,
        'receitas_json': receitas_json,
        'ficha': ficha,
    })

def excluir_ficha_tecnica(request, pk):
    ficha = get_object_or_404(FichaTecnica, pk=pk)
    if request.user.role in ['standard', 'master']:
        raise PermissionDenied("Você não tem permissão para excluir fichas técnicas.")
    restaurante_id = ficha.restaurante.id
    ficha.delete()
    return redirect('restaurante:restaurante_detail', pk=restaurante_id)

@login_required
def detalhe_ficha_tecnica(request, ficha_id):
    """
    Exibe os detalhes da ficha técnica.
    - Usuários com papel 'admin' e 'master' visualizam todas as informações, inclusive valores.
    - Usuários 'standard' não visualizam informações relacionadas a preços.
    """
    ficha = get_object_or_404(FichaTecnica, pk=ficha_id)
    
    show_prices = request.user.role in ['admin', 'master']
    show_fator_correcao = request.user.role == 'admin'
    
    # Obtemos o parâmetro calc_unit para a exibição; default: 'g'
    calc_unit = request.GET.get('calc_unit', 'g').lower()
    
    context = {
        'ficha': ficha,
        'valor_venda_sugerida': ficha.valor_venda_sugerida,
        'show_prices': show_prices,
        'show_fator_correcao': show_fator_correcao,
        'calc_unit': calc_unit,  # Passa a unidade utilizada na entrada para o template
    }
    return render(request, 'fichas_tecnicas/detalhe_ficha_tecnica.html', context)

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
