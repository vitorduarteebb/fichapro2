# Generated by Django 5.1.5 on 2025-03-04 05:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fichas_tecnicas', '0006_alter_fichatecnicainsumo_ajuste_tipo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fichatecnicainsumo',
            name='ajuste_tipo',
            field=models.CharField(blank=True, help_text="Informe 'fc' para IC ou 'ipc' para IPC", max_length=10, null=True, verbose_name='TIPO DE AJUSTE'),
        ),
    ]
