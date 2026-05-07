#!/bin/bash
set -e

echo "=== Información de conexión a PostgreSQL ==="
echo "DB_HOST: $DB_HOST"
echo "DB_PORT: $DB_PORT"
echo "DB_NAME: $DB_NAME"
echo "DB_USER: $DB_USER"
echo "==========================================="

# Intentar resolver el hostname
echo "Intentando resolver hostname..."
nslookup $DB_HOST || echo "⚠️  No se pudo resolver el hostname con nslookup"
ping -c 1 $DB_HOST || echo "⚠️  No se pudo hacer ping al host"

echo "Esperando a que PostgreSQL esté disponible..."
# Primero esperar a que el servidor PostgreSQL esté listo
MAX_RETRIES=30
RETRY_COUNT=0

# Intentar conectar al servidor PostgreSQL (usando postgres database por defecto)
until PGPASSWORD=${DB_PASSWORD:-postgres} psql -h "$DB_HOST" -U "${DB_USER:-postgres}" -d "postgres" -c '\q' 2>/dev/null; do
  RETRY_COUNT=$((RETRY_COUNT + 1))
  if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    echo "❌ ERROR: No se pudo conectar al servidor PostgreSQL después de $MAX_RETRIES intentos"
    echo ""
    echo "Diagnóstico:"
    echo "  - Verificar que la base de datos esté ejecutándose"
    echo "  - Verificar que ambos contenedores estén en la misma red Docker"
    echo "  - Verificar las credenciales de la base de datos"
    echo ""
    exit 1
  fi
  echo "PostgreSQL no está disponible - esperando... (intento $RETRY_COUNT/$MAX_RETRIES)"
  sleep 2
done

echo "✓ Servidor PostgreSQL está disponible!"

# Verificar si la base de datos existe, si no, crearla
echo "Verificando si la base de datos '$DB_NAME' existe..."
if ! PGPASSWORD=${DB_PASSWORD:-postgres} psql -h "$DB_HOST" -U "${DB_USER:-postgres}" -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo "Base de datos '$DB_NAME' no existe. Intentando crearla..."
    PGPASSWORD=${DB_PASSWORD:-postgres} psql -h "$DB_HOST" -U "${DB_USER:-postgres}" -d "postgres" -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || echo "⚠️  No se pudo crear la base de datos (puede que ya exista o no tengas permisos)"
fi

# Ahora intentar conectar a la base de datos específica
RETRY_COUNT=0
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; do
  RETRY_COUNT=$((RETRY_COUNT + 1))
  if [ $RETRY_COUNT -ge 10 ]; then
    echo "❌ ERROR: No se pudo conectar a la base de datos '$DB_NAME'"
    echo "Verifica que el usuario '$DB_USER' tenga permisos en la base de datos '$DB_NAME'"
    exit 1
  fi
  echo "Esperando conexión a la base de datos '$DB_NAME'... (intento $RETRY_COUNT/10)"
  sleep 2
done

echo "✓ Conectado exitosamente a la base de datos '$DB_NAME'!"

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
