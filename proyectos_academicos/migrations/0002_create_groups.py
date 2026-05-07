from django.db import migrations


def create_groups(apps, schema_editor):
    """
    Crea los grupos 'estudiante' y 'docente' necesarios para el control de acceso.
    Requisitos: 1.4
    """
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='estudiante')
    Group.objects.get_or_create(name='docente')


def delete_groups(apps, schema_editor):
    """
    Elimina los grupos creados (operación inversa).
    """
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=['estudiante', 'docente']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('proyectos_academicos', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_groups, delete_groups),
    ]
