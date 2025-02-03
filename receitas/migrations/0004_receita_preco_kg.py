# Generated by Django 5.1.5 on 2025-02-03 00:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('receitas', '0003_receita_modo_preparo_alter_receita_data_criacao_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='receita',
            name='preco_kg',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Preço do KG (R$)'),
        ),
    ]
