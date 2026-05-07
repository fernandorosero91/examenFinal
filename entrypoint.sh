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

echo "Iniciando servidor Gunicorn..."
exec gunicorn evaluaciones__nombre__estudiantes.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
