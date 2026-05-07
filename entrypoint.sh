#!/bin/bash
set -e

echo "Esperando a que PostgreSQL esté disponible..."
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; do
  echo "PostgreSQL no está disponible - esperando..."
  sleep 2
done

echo "PostgreSQL está disponible!"

echo "Aplicando migraciones..."
python manage.py migrate --noinput

echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

# Crear superusuario si las variables están definidas
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creando superusuario..."
    python manage.py createsuperuser --noinput 2>/dev/null || echo "Superusuario ya existe."
fi

# Crear grupos y usuarios de prueba
echo "Configurando grupos y usuarios de prueba..."
python manage.py shell <<EOF
from django.contrib.auth.models import User, Group
import os

# Crear grupos si no existen
grupo_estudiante, created = Group.objects.get_or_create(name='estudiante')
if created:
    print("✓ Grupo 'estudiante' creado")
else:
    print("✓ Grupo 'estudiante' ya existe")

grupo_docente, created = Group.objects.get_or_create(name='docente')
if created:
    print("✓ Grupo 'docente' creado")
else:
    print("✓ Grupo 'docente' ya existe")

# Crear usuario docente de prueba
docente_username = os.getenv('DOCENTE_USERNAME', 'docente')
docente_email = os.getenv('DOCENTE_EMAIL', 'docente@example.com')
docente_password = os.getenv('DOCENTE_PASSWORD', 'docente123')

if not User.objects.filter(username=docente_username).exists():
    docente = User.objects.create_user(
        username=docente_username,
        email=docente_email,
        password=docente_password,
        first_name='Docente',
        last_name='Prueba'
    )
    docente.groups.add(grupo_docente)
    print(f"✓ Usuario docente '{docente_username}' creado")
else:
    print(f"✓ Usuario docente '{docente_username}' ya existe")

# Crear usuario estudiante de prueba
estudiante_username = os.getenv('ESTUDIANTE_USERNAME', 'estudiante')
estudiante_email = os.getenv('ESTUDIANTE_EMAIL', 'estudiante@example.com')
estudiante_password = os.getenv('ESTUDIANTE_PASSWORD', 'estudiante123')

if not User.objects.filter(username=estudiante_username).exists():
    estudiante = User.objects.create_user(
        username=estudiante_username,
        email=estudiante_email,
        password=estudiante_password,
        first_name='Estudiante',
        last_name='Prueba'
    )
    estudiante.groups.add(grupo_estudiante)
    print(f"✓ Usuario estudiante '{estudiante_username}' creado")
else:
    print(f"✓ Usuario estudiante '{estudiante_username}' ya existe")

print("✓ Configuración de usuarios completada")
EOF

echo "Iniciando servidor Gunicorn..."
exec gunicorn proyecto_fernando.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
