# Generated by Django 5.1.5 on 2025-01-31 01:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('restaurante', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Insumo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255, unique=True)),
                ('quantidade', models.DecimalField(decimal_places=2, max_digits=10)),
                ('unidade_de_medida', models.CharField(choices=[('KG', 'Kilograma'), ('G', 'Grama'), ('L', 'Litro'), ('ML', 'Mililitro'), ('UN', 'Unidade')], max_length=9)),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10)),
                ('restaurante', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='restaurante.restaurante')),
            ],
        ),
    ]
