from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import xml.etree.ElementTree as ET
from django.forms import modelformset_factory
from django.db import IntegrityError

from .models import Insumo
from .forms import ImportXMLForm, InsumoForm, ImportInsumoForm
from restaurante.models import Restaurante

def import_insumos(request, restaurante_id):
    """
    Exibe o formulário para upload do XML, processa o arquivo para extrair os dados
    dos insumos e armazena esses dados na sessão para confirmação.
    """
    restaurante = get_object_or_404(Restaurante, pk=restaurante_id)
    
    if request.method == 'POST' and 'xml_file' in request.FILES:
        form = ImportXMLForm(request.POST, request.FILES)
        if form.is_valid():
            xml_file = request.FILES['xml_file']
            try:
                xml_file.seek(0)
                xml_content = xml_file.read()
                if isinstance(xml_content, bytes):
                    xml_content = xml_content.decode('utf-8')
                root = ET.fromstring(xml_content)
                # Remover namespaces (se houver)
                for elem in root.iter():
                    if '}' in elem.tag:
                        elem.tag = elem.tag.split('}', 1)[1]
            except Exception as e:
                form.add_error('xml_file', f"Erro ao ler o arquivo XML: {e}")
                return render(request, "insumos/import_insumos.html", {"form": form, "restaurante": restaurante})
            
            insumos_data = []
            # Procura os itens dentro do nó <infNFe>
            for det in root.findall(".//infNFe/det"):
                prod = det.find("prod")
                if prod is not None:
                    nome = prod.findtext("xProd", "").strip()
                    unidade = prod.findtext("uCom", "").strip().lower()
                    quantidade_str = prod.findtext("qCom", "0").strip()
                    preco_str = prod.findtext("vUnCom", "0").strip()
                    
                    try:
                        quantidade = Decimal(quantidade_str).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    except InvalidOperation:
                        quantidade = Decimal("0.00")
                    try:
                        preco = Decimal(preco_str).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    except InvalidOperation:
                        preco = Decimal("0.00")
                    
                    peso = str(quantidade) if unidade in ['kg', 'g'] else ""
                    
                    if nome:
                        insumos_data.append({
                            "nome": nome,
                            "unidade_medida": unidade,
                            "quantidade": str(quantidade),
                            "preco": str(preco),
                            "peso": peso,
                        })
            
            print("Número de itens extraídos:", len(insumos_data))
            
            request.session['insumos_import_data'] = insumos_data
            request.session['import_restaurante_id'] = restaurante.id
            # Redireciona para a tela de confirmação (em seguida, após confirmar, voltará para o restaurante)
            return redirect(reverse('insumos:confirmar_import_insumos'))
    else:
        form = ImportXMLForm()
    
    return render(request, "insumos/import_insumos.html", {"form": form, "restaurante": restaurante})


def confirmar_import_insumos(request):
    """
    Exibe um modelformset para que o usuário revise, edite ou exclua os insumos importados.
    Ao confirmar, os insumos são salvos (usando update_or_create ou tratando IntegrityError)
    e associados ao restaurante.
    Após o cadastro, redireciona para a tela do restaurante.
    """
    restaurante_id = request.session.get('import_restaurante_id')
    restaurante = get_object_or_404(Restaurante, pk=restaurante_id)
    insumos_data = request.session.get('insumos_import_data', [])
    
    if request.method == 'POST':
        InsumoFormSet = modelformset_factory(Insumo, form=ImportInsumoForm, extra=0, can_delete=True)
        formset = InsumoFormSet(request.POST, queryset=Insumo.objects.none())
        if formset.is_valid():
            print("Formset cleaned_data:", formset.cleaned_data)
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    data = form.cleaned_data
                    try:
                        data['quantidade'] = Decimal(data.get('quantidade', '0')).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    except Exception:
                        data['quantidade'] = Decimal("0.00")
                    try:
                        data['preco'] = Decimal(data.get('preco', '0')).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                    except Exception:
                        data['preco'] = Decimal("0.00")
                    if data.get('peso'):
                        try:
                            data['peso'] = Decimal(data.get('peso')).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                        except Exception:
                            data['peso'] = None
                    else:
                        data['peso'] = None

                    defaults = {
                        'unidade_medida': data['unidade_medida'],
                        'quantidade': data['quantidade'],
                        'preco': data['preco'],
                        'peso': data['peso'],
                    }
                    try:
                        insumo, created = Insumo.objects.update_or_create(
                            nome=data['nome'],
                            restaurante=restaurante,
                            defaults=defaults
                        )
                    except IntegrityError:
                        insumo = Insumo.objects.get(nome=data['nome'])
                        insumo.restaurante = restaurante
                        insumo.unidade_medida = data['unidade_medida']
                        insumo.quantidade = data['quantidade']
                        insumo.preco = data['preco']
                        insumo.peso = data['peso']
                        insumo.save()
            request.session.pop('insumos_import_data', None)
            request.session.pop('import_restaurante_id', None)
            # Após confirmar, redireciona para a tela do restaurante
            return redirect(reverse('restaurante:restaurante_detail', args=[restaurante.id]))
        else:
            print("Erros do formset:", formset.errors)
    else:
        extra = len(insumos_data)
        InsumoFormSet = modelformset_factory(Insumo, form=ImportInsumoForm, extra=extra, can_delete=True)
        formset = InsumoFormSet(queryset=Insumo.objects.none(), initial=insumos_data)
    
    return render(request, "insumos/confirm_import_insumos.html", {
        "formset": formset,
        "restaurante": restaurante
    })


def cadastro_insumo(request, restaurante_id):
    """
    Cadastra um insumo associado a um restaurante (via formulário manual).
    Após o cadastro, redireciona para a tela do restaurante.
    """
    restaurante = get_object_or_404(Restaurante, pk=restaurante_id)
    if request.method == 'POST':
        form = InsumoForm(request.POST)
        if form.is_valid():
            insumo = form.save(commit=False)
            insumo.restaurante = restaurante
            insumo.save()
            return redirect(reverse('restaurante:restaurante_detail', args=[restaurante.id]))
    else:
        form = InsumoForm()
    
    return render(request, "insumos/cadastro_insumo.html", {"form": form, "restaurante": restaurante})


def lista_insumos(request):
    """
    Lista todos os insumos cadastrados.
    """
    insumos = Insumo.objects.all()
    return render(request, "insumos/lista_insumos.html", {"insumos": insumos})


def excluir_insumo(request, pk):
    insumo = get_object_or_404(Insumo, pk=pk)
    restaurante_id = insumo.restaurante.id  # Certifique-se de que o modelo Insumo tem uma FK para Restaurante
    insumo.delete()
    return redirect('restaurante:restaurante_detail', pk=restaurante_id)

