from django.db import migrations

def set_restaurante_null(apps, schema_editor):
    Insumo = apps.get_model('insumos', 'Insumo')
    # Atualiza todos os insumos existentes para definir restaurante_id como None
    Insumo.objects.all().update(restaurante=None)

class Migration(migrations.Migration):

    dependencies = [
        ('insumos', '0003_insumo_restaurante'),  # ajuste para a migração anterior correta
    ]

    operations = [
        migrations.RunPython(set_restaurante_null),
    ]
