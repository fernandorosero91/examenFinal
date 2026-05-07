FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema necesarias para PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt primero
COPY requirements.txt /app/requirements.txt

# Instalar dependencias Python
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copiar el resto del proyecto
COPY . /app/

# Crear directorio para archivos estáticos
RUN mkdir -p /app/staticfiles

# Dar permisos al entrypoint
RUN chmod +x /app/entrypoint.sh

# El WORKDIR debe ser /app donde está manage.py
WORKDIR /app

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
