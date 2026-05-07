#!/bin/bash
set -e

echo "=== Información de conexión a PostgreSQL ==="
echo "DB_HOST: $DB_HOST"
echo "DB_PORT: $DB_PORT"
echo "DB_NAME: $DB_NAME"
echo "DB_USER: $DB_USER"
echo "==========================================="

# Función para probar conectividad
test_postgres() {
    PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null
}

# Función para probar conectividad con timeout
test_postgres_with_timeout() {
    timeout 5 bash -c "PGPASSWORD=$DB_PASSWORD psql -h '$DB_HOST' -U '$DB_USER' -d '$DB_NAME' -c '\q'" 2>/dev/null
}

echo "Esperando a que PostgreSQL esté disponible..."
MAX_RETRIES=60
RETRY_COUNT=0

while ! test_postgres_with_timeout; do
  RETRY_COUNT=$((RETRY_COUNT + 1))
  if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    echo "⚠️  WARNING: No se pudo conectar a PostgreSQL después de $MAX_RETRIES intentos"
    echo ""
    echo "Probando hosts alternativos..."
    
    # Lista de hosts alternativos específicos para DocPloy
    for alt_host in "postgres" "postgresql" "db" "database" "examenfinal-examen-ziqe1h" "localhost" "127.0.0.1"; do
        echo "Probando host alternativo: $alt_host"
        if timeout 5 bash -c "PGPASSWORD=$DB_PASSWORD psql -h '$alt_host' -U '$DB_USER' -d '$DB_NAME' -c '\q'" 2>/dev/null; then
            echo "✅ ¡Conexión exitosa con $alt_host!"
            export DB_HOST=$alt_host
            break
        fi
    done
    
    # Si aún no funciona, usar SQLite
    if ! test_postgres_with_timeout; then
        echo "❌ No se pudo conectar a PostgreSQL con ningún host"
        echo "🔄 Usando SQLite como fallback..."
        export USE_SQLITE=true
        unset DB_NAME DB_USER DB_PASSWORD DB_HOST DB_PORT
        echo "✓ Configurado para usar SQLite"
    fi
    break
  fi
  echo "PostgreSQL no está disponible - esperando... (intento $RETRY_COUNT/$MAX_RETRIES)"
  sleep 1
done

if [ "$USE_SQLITE" != "true" ]; then
    echo "✅ PostgreSQL está disponible en: $DB_HOST"
fi

echo "🔄 Aplicando migraciones..."
python manage.py migrate --noinput || {
    echo "❌ Error en migraciones, intentando con SQLite..."
    export USE_SQLITE=true
    unset DB_NAME DB_USER DB_PASSWORD DB_HOST DB_PORT
    python manage.py migrate --noinput
}

echo "📁 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

# Crear superusuario si las variables están definidas
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "👤 Creando superusuario..."
    python manage.py createsuperuser --noinput 2>/dev/null || echo "✓ Superusuario ya existe."
fi

# Crear grupos y usuarios de prueba
echo "👥 Configurando grupos y usuarios de prueba..."
python manage.py shell <<'EOF'
from django.contrib.auth.models import User, Group
import os

try:
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
except Exception as e:
    print(f"⚠️  Error al configurar usuarios: {e}")
    print("Continuando con el inicio del servidor...")
EOF

# Verificar configuración antes de iniciar
echo "🔍 Verificando configuración..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_fernando.settings')
django.setup()
from django.conf import settings
print(f'DEBUG: {settings.DEBUG}')
print(f'ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}')
print(f'DATABASE ENGINE: {settings.DATABASES[\"default\"][\"ENGINE\"]}')
"

echo ""
echo "========================================="
echo "✅ Inicialización completada"
if [ "$USE_SQLITE" = "true" ]; then
    echo "⚠️  Usando SQLite (PostgreSQL no disponible)"
else
    echo "✅ Usando PostgreSQL"
fi
echo "========================================="
echo ""
echo "🚀 Iniciando servidor Gunicorn..."

# Iniciar Gunicorn con archivo de configuración
exec gunicorn -c gunicorn.conf.py proyecto_fernando.wsgi:application