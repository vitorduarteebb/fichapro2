# Generated by Django 5.1.5 on 2025-02-01 22:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insumos', '0002_rename_valor_insumo_preco_remove_insumo_restaurante_and_more'),
        ('restaurante', '0002_remove_restaurante_criado_em_remove_restaurante_nome_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='insumo',
            name='restaurante',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='insumos', to='restaurante.restaurante', verbose_name='Restaurante'),
            preserve_default=False,
        ),
    ]
