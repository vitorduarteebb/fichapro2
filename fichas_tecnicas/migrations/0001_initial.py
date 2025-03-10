# Generated by Django 5.1.6 on 2025-03-08 12:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('insumos', '0001_initial'),
        ('receitas', '0001_initial'),
        ('restaurante', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FichaTecnica',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome_prato', models.CharField(default='FICHA TÉCNICA SEM NOME', max_length=255, verbose_name='NOME DO PRATO')),
                ('imagem', models.ImageField(blank=True, null=True, upload_to='fichas_tecnicas_imagens/', verbose_name='IMAGEM DO PRATO')),
                ('porcao_sugerida', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='PORÇÃO SUGERIDA (EM GRAMAS)')),
                ('tempo_preparo', models.IntegerField(verbose_name='TEMPO DE PREPARO (MIN)')),
                ('modo_preparo', models.TextField(blank=True, verbose_name='MODO DE PREPARO')),
                ('peso_total', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='PESO TOTAL DA PREPARAÇÃO (G)')),
                ('custo_total_insumos', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='CUSTO TOTAL DOS INSUMOS (R$)')),
                ('custo_total_receitas', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='CUSTO TOTAL DAS RECEITAS (R$)')),
                ('valor_venda_sugerida', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='VALOR DE VENDA SUGERIDA (R$)')),
                ('valor_trabalhado', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='VALOR TRABALHADO (R$)')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='DATA DE CADASTRO')),
                ('restaurante', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fichas_tecnicas', to='restaurante.restaurante')),
            ],
        ),
        migrations.CreateModel(
            name='FichaTecnicaInsumo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade_utilizada', models.DecimalField(decimal_places=2, help_text='Informe a quantidade utilizada (na mesma unidade do insumo)', max_digits=10, verbose_name='QUANTIDADE UTILIZADA')),
                ('ajuste_tipo', models.CharField(blank=True, help_text="Informe 'fc' para IC ou 'ipc' para IPC", max_length=10, null=True, verbose_name='TIPO DE AJUSTE')),
                ('ajuste_sinal', models.CharField(blank=True, help_text="Informe 'mais' ou 'menos'", max_length=10, null=True, verbose_name='SINAL DO AJUSTE')),
                ('ajuste_percentual', models.DecimalField(blank=True, decimal_places=2, help_text='Ex.: 70 para 70%', max_digits=5, null=True, verbose_name='PERCENTUAL DE AJUSTE (%)')),
                ('custo_utilizado', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='CUSTO UTILIZADO (R$)')),
                ('ficha_tecnica', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itens_insumos', to='fichas_tecnicas.fichatecnica')),
                ('insumo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='insumos.insumo')),
            ],
        ),
        migrations.CreateModel(
            name='FichaTecnicaReceita',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade_utilizada', models.DecimalField(decimal_places=2, help_text='Informe a quantidade utilizada da receita na ficha (na unidade escolhida)', max_digits=10, verbose_name='QUANTIDADE UTILIZADA')),
                ('unidade', models.CharField(default='g', max_length=10, verbose_name='UNIDADE')),
                ('custo_utilizado', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='CUSTO UTILIZADO (R$)')),
                ('ficha_tecnica', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itens_receitas', to='fichas_tecnicas.fichatecnica')),
                ('receita', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='receitas.receita')),
            ],
        ),
    ]
