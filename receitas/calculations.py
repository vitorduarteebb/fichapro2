# receitas/calculations.py
from decimal import Decimal, ROUND_HALF_UP

def convert_quantity(value, from_unit, to_unit):
    """
    Converte um valor de uma unidade para outra (suporta kg e g).
    """
    if from_unit.lower() == to_unit.lower():
        return value
    if from_unit.lower() == 'kg' and to_unit.lower() == 'g':
        return value * Decimal("1000")
    if from_unit.lower() == 'g' and to_unit.lower() == 'kg':
        return value / Decimal("1000")
    return value

def calculate_base_cost(insumo, quantidade, unit_used):
    """
    Calcula o custo base do insumo, convertendo a quantidade para a unidade padrão do insumo.
    """
    if insumo.preco and insumo.quantidade:
        quantidade_convertida = convert_quantity(quantidade, unit_used, insumo.unidade_medida)
        return (quantidade_convertida * insumo.preco) / Decimal(insumo.quantidade)
    return Decimal("0.00")

def apply_adjustment(base_cost, ajuste_tipo=None, ajuste_sinal='mais', ajuste_percentual=Decimal("0")):
    """
    Aplica o ajuste sobre o custo base:
      - 'fc' (FATOR DE CORREÇÃO IC): aumenta ou reduz percentual.
      - 'ipc' (IPC): multiplica por (100 / ajuste_percentual).
    """
    final_cost = base_cost
    if ajuste_tipo == 'fc' and ajuste_percentual:
        if ajuste_sinal == 'mais':
            final_cost = base_cost * (1 + ajuste_percentual / Decimal("100"))
        elif ajuste_sinal == 'menos':
            final_cost = base_cost * (1 - ajuste_percentual / Decimal("100"))
    elif ajuste_tipo == 'ipc' and ajuste_percentual and ajuste_percentual != Decimal("0"):
        final_cost = base_cost * (Decimal("100") / ajuste_percentual)
    return final_cost.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def calculate_final_cost(insumo, quantidade, unit_used, ajuste_tipo=None, ajuste_sinal='mais', ajuste_percentual=Decimal("0")):
    """
    Calcula o custo final:
      1. Converte a quantidade e calcula o custo base.
      2. Aplica o ajuste (se houver).
    """
    base_cost = calculate_base_cost(insumo, quantidade, unit_used)
    return apply_adjustment(base_cost, ajuste_tipo, ajuste_sinal, ajuste_percentual)
