import json
from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import inlineformset_factory
from .models import FichaTecnica, FichaTecnicaInsumo, FichaTecnicaReceita
from .forms import FichaTecnicaForm, FichaTecnicaInsumoForm, FichaTecnicaReceitaForm
from restaurante.models import Restaurante
from insumos.models import Insumo
from receitas.models import Receita

def ficha_tecnica_cadastro(request, restaurante_id):
    restaurante = get_object_or_404(Restaurante, pk=restaurante_id)
    FichaInsumoFormSet = inlineformset_factory(FichaTecnica, FichaTecnicaInsumo, form=FichaTecnicaInsumoForm, extra=1, can_delete=True)
    FichaReceitaFormSet = inlineformset_factory(FichaTecnica, FichaTecnicaReceita, form=FichaTecnicaReceitaForm, extra=1, can_delete=True)
    
    insumos = Insumo.objects.all()
    insumos_json = json.dumps([
        {'id': insumo.id, 'preco': str(insumo.preco), 'unidade': insumo.unidade_medida}
        for insumo in insumos
    ])
    receitas = Receita.objects.all()
    receitas_json = json.dumps([
        {'id': receita.id, 'preco_kg': str(receita.preco_kg if receita.preco_kg is not None else "0.00")}
        for receita in receitas
    ])
    
    if request.method == 'POST':
        form = FichaTecnicaForm(request.POST, request.FILES)
        formset_insumos = FichaInsumoFormSet(request.POST, prefix='insumos')
        formset_receitas = FichaReceitaFormSet(request.POST, prefix='receitas')
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
                    var_unidade = item_form.cleaned_data.get('unidade', 'kg').lower()
                    # Converter para gramas se a unidade selecionada for 'kg' e o insumo estiver em kg
                    if ficha_insumo.insumo.unidade_medida.lower() == 'kg':
                        total_peso += ficha_insumo.quantidade_utilizada * Decimal("1000")
                    else:
                        total_peso += ficha_insumo.quantidade_utilizada
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
            
            ficha.peso_total = total_peso.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ficha.custo_total_insumos = total_custo_insumos.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ficha.custo_total_receitas = total_custo_receitas.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ficha.valor_venda_sugerida = ((ficha.custo_total_insumos + ficha.custo_total_receitas) * restaurante.fator_correcao_financeiro).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ficha.save()
            return redirect('restaurante:restaurante_detail', pk=restaurante.id)
    else:
        form = FichaTecnicaForm()
        formset_insumos = FichaInsumoFormSet(prefix='insumos')
        formset_receitas = FichaReceitaFormSet(prefix='receitas')
    
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
