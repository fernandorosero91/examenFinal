# Sistema de Gestión de Proyectos Académicos

Sistema web desarrollado en Django para la gestión de proyectos académicos entre estudiantes y docentes. Permite el envío, revisión, calificación y retroalimentación de trabajos académicos con notificaciones por correo electrónico.

## 🚀 Características

- **Autenticación basada en roles**: Estudiantes y Docentes con permisos diferenciados
- **Gestión de proyectos**: Crear, editar, eliminar y revisar proyectos académicos
- **Sistema de estados**: Flujo de trabajo con estados (Enviado → En Revisión → Aprobado)
- **Comentarios y retroalimentación**: Sistema de comentarios con notificaciones por email
- **Validaciones de negocio**: Solo archivos PDF, calificaciones 0.0-5.0, restricciones por estado
- **Panel de estadísticas**: Métricas agregadas para docentes
- **Exportación de reportes**: Generación de reportes en CSV y PDF
- **Interfaz responsive**: Diseño moderno con Tailwind CSS

## 📋 Requisitos Previos

- Python 3.10 o superior
- pip (gestor de paquetes de Python)
- Git (opcional, para clonar el repositorio)
- PostgreSQL (opcional, para producción)

## ⚡ Inicio Rápido (Desarrollo)

Si solo quiere probar el sistema rápidamente en desarrollo:

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd proyecto_fernando

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Aplicar migraciones
python manage.py migrate

# 5. Crear superusuario
python manage.py createsuperuser

# 6. Ejecutar servidor
python manage.py runserver
```

Acceda a: http://127.0.0.1:8000/

**Nota**: En desarrollo, el sistema usa SQLite automáticamente. No necesita configurar PostgreSQL ni variables de entorno.

## 🔧 Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd proyecto_fernando
```

### 2. Crear entorno virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno (Opcional para desarrollo)

**Para desarrollo local**, el sistema funciona con configuración por defecto (SQLite y console email backend). **No necesita crear un archivo `.env`** para desarrollo.

Si desea personalizar la configuración de desarrollo, puede crear un archivo `.env`:

```bash
cp .env.local .env
```

El archivo `.env.local` contiene configuración para desarrollo:
- `DEBUG=True`
- SQLite (sin variables DB_*)
- Console email backend

**Para producción**, copie el archivo de ejemplo y configure las variables:

```bash
cp .env.example .env
```

Edite el archivo `.env` con sus valores de producción:

```env
SECRET_KEY=tu-clave-secreta-generada
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
CSRF_TRUSTED_ORIGINS=https://tu-dominio.com

# PostgreSQL (requerido en producción)
DB_NAME=proyectos_academicos_db
DB_USER=proyectos_user
DB_PASSWORD=tu-password-seguro
DB_HOST=localhost
DB_PORT=5432

# Email SMTP (para notificaciones)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-password-de-aplicacion
DEFAULT_FROM_EMAIL=tu-email@gmail.com
```

**IMPORTANTE**: 
- Si el archivo `.env` contiene variables `DB_NAME`, `DB_USER`, etc., Django intentará conectarse a PostgreSQL
- Para desarrollo con SQLite, **NO incluya** las variables de base de datos en `.env` o déjelas vacías
- El archivo `.env` está en `.gitignore` y no se incluirá en el control de versiones

### 5. Aplicar migraciones

```bash
python manage.py migrate
```

### 6. Crear grupos de usuarios

El sistema requiere dos grupos: **estudiante** y **docente**. Estos se crean automáticamente con la migración `0002_create_groups.py`.

**En producción con Docker/entrypoint.sh**: Los grupos se crean automáticamente al iniciar el contenedor.

Para verificar que los grupos existen:

```bash
python manage.py shell
>>> from django.contrib.auth.models import Group
>>> Group.objects.all()
<QuerySet [<Group: estudiante>, <Group: docente>]>
>>> exit()
```

### 7. Crear superusuario

**Opción 1: Manualmente**

```bash
python manage.py createsuperuser
```

Siga las instrucciones para crear el usuario administrador.

**Opción 2: Con variables de entorno (Recomendado para producción)**

Configure las variables en `.env`:

```env
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=tu-password-seguro
```

Luego ejecute:

```bash
python manage.py createsuperuser --noinput
```

**Opción 3: Automático con Docker/entrypoint.sh**

Si usa Docker, el superusuario se crea automáticamente al iniciar el contenedor si las variables están configuradas.

### 8. Crear usuarios de prueba (Opcional)

**Opción 1: Con variables de entorno (Recomendado)**

Configure las variables en `.env`:

```env
# Usuario Docente
DOCENTE_USERNAME=docente
DOCENTE_EMAIL=docente@example.com
DOCENTE_PASSWORD=docente123

# Usuario Estudiante
ESTUDIANTE_USERNAME=estudiante
ESTUDIANTE_EMAIL=estudiante@example.com
ESTUDIANTE_PASSWORD=estudiante123
```

Si usa Docker/entrypoint.sh, estos usuarios se crean automáticamente al iniciar el contenedor.

**Opción 2: Manualmente desde el shell**

Puede crear usuarios desde el panel de administración de Django o mediante el shell:

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User, Group

# Crear grupo estudiante y docente (si no existen)
grupo_estudiante, _ = Group.objects.get_or_create(name='estudiante')
grupo_docente, _ = Group.objects.get_or_create(name='docente')

# Crear un estudiante
estudiante = User.objects.create_user(
    username='estudiante1',
    email='estudiante1@example.com',
    password='password123',
    first_name='Juan',
    last_name='Pérez'
)
estudiante.groups.add(grupo_estudiante)

# Crear un docente
docente = User.objects.create_user(
    username='docente1',
    email='docente1@example.com',
    password='password123',
    first_name='María',
    last_name='García'
)
docente.groups.add(grupo_docente)

exit()
```

exit()
```

### 9. Ejecutar el servidor de desarrollo

```bash
python manage.py runserver
```

Acceda a la aplicación en: http://127.0.0.1:8000/

## 👥 Usuarios y Roles

### Estudiante
- **Permisos**:
  - Crear proyectos propios
  - Editar proyectos propios (solo si estado != "aprobado")
  - Eliminar proyectos propios (solo si estado == "enviado")
  - Ver solo sus propios proyectos
  - Agregar comentarios a sus proyectos (si estado != "aprobado")

### Docente
- **Permisos**:
  - Ver todos los proyectos
  - Editar cualquier proyecto
  - Cambiar estado de proyectos (enviado, revisión, aprobado)
  - Asignar calificaciones (0.0 - 5.0)
  - Agregar comentarios a cualquier proyecto
  - Acceder al panel de estadísticas
  - Exportar reportes CSV y PDF

## 📁 Estructura del Proyecto

```
proyecto_fernando/
├── manage.py                      # Script de gestión de Django
├── requirements.txt               # Dependencias de Python
├── .env.example                   # Plantilla de variables de entorno
├── README.md                      # Este archivo
├── db.sqlite3                     # Base de datos SQLite (desarrollo)
│
├── proyecto_fernando/             # Configuración del proyecto
│   ├── settings.py                # Configuración principal
│   ├── urls.py                    # URLs principales
│   └── wsgi.py                    # Punto de entrada WSGI
│
├── proyectos_academicos/          # Aplicación principal
│   ├── models.py                  # Modelos (Proyecto, Comentario)
│   ├── views.py                   # Vistas (CBVs y FBVs)
│   ├── forms.py                   # Formularios
│   ├── urls.py                    # URLs de la aplicación
│   ├── admin.py                   # Configuración del admin
│   ├── signals.py                 # Signals para notificaciones
│   └── migrations/                # Migraciones de base de datos
│       ├── 0001_initial.py        # Migración inicial
│       └── 0002_create_groups.py  # Creación de grupos
│
├── templates/                     # Plantillas HTML
│   ├── base.html                  # Plantilla base
│   ├── dashboard.html             # Dashboard principal
│   ├── estadisticas.html          # Panel de estadísticas
│   ├── proyectos/                 # Templates de proyectos
│   │   ├── proyecto_list.html
│   │   ├── proyecto_form.html
│   │   ├── proyecto_detail.html
│   │   └── proyecto_confirm_delete.html
│   ├── partials/                  # Componentes reutilizables
│   │   ├── badge_estado.html
│   │   ├── botones_accion.html
│   │   └── alerta.html
│   └── registration/
│       └── login.html             # Página de login
│
└── media/                         # Archivos subidos por usuarios
    └── proyectos/                 # PDFs de proyectos
```

## 🔐 Seguridad

### Variables de Entorno

**IMPORTANTE**: Nunca incluya el archivo `.env` en el control de versiones. El archivo `.gitignore` ya lo excluye por defecto.

### Secret Key

Genere una clave secreta única para producción:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Contraseñas de Email

Para Gmail, use **Contraseñas de Aplicación** en lugar de su contraseña principal:
1. Vaya a https://myaccount.google.com/security
2. Active la verificación en dos pasos
3. Genere una contraseña de aplicación
4. Use esa contraseña en `EMAIL_HOST_PASSWORD`

## 🚀 Despliegue en Producción

### 1. Configurar variables de entorno

Copie `.env.example` a `.env` y configure todas las variables para producción:

```bash
cp .env.example .env
nano .env  # o use su editor preferido
```

**Variables críticas**:
- `SECRET_KEY`: Genere una clave única y segura
- `DEBUG=False`: Desactive el modo debug
- `ALLOWED_HOSTS`: Configure sus dominios
- `CSRF_TRUSTED_ORIGINS`: Configure sus URLs con https://
- `DB_*`: Configure PostgreSQL (recomendado)
- `EMAIL_*`: Configure SMTP para notificaciones
- `DJANGO_SUPERUSER_*`: Configure credenciales del superusuario
- `DOCENTE_*` y `ESTUDIANTE_*`: (Opcional) Usuarios de prueba

### 2. Instalar dependencias de producción

```bash
pip install -r requirements.txt
```

Esto incluye:
- `psycopg2-binary`: Driver de PostgreSQL
- `gunicorn`: Servidor WSGI
- `whitenoise`: Servidor de archivos estáticos
- `python-dotenv`: Carga de variables de entorno

### 3. Configurar base de datos PostgreSQL

```bash
# Crear base de datos y usuario en PostgreSQL
sudo -u postgres psql

CREATE DATABASE proyectos_academicos_db;
CREATE USER proyectos_user WITH PASSWORD 'tu-password-seguro';
ALTER ROLE proyectos_user SET client_encoding TO 'utf8';
ALTER ROLE proyectos_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE proyectos_user SET timezone TO 'America/Bogota';
GRANT ALL PRIVILEGES ON DATABASE proyectos_academicos_db TO proyectos_user;
\q
```

### 4. Aplicar migraciones

```bash
python manage.py migrate
```

### 5. Crear superusuario

```bash
python manage.py createsuperuser
```

O use variables de entorno para creación automática:

```bash
export DJANGO_SUPERUSER_USERNAME=admin
export DJANGO_SUPERUSER_EMAIL=admin@example.com
export DJANGO_SUPERUSER_PASSWORD=tu-password-seguro
python manage.py createsuperuser --noinput
```

### 6. Recolectar archivos estáticos

```bash
python manage.py collectstatic --noinput
```

### 7. Ejecutar con Gunicorn

```bash
gunicorn proyecto_fernando.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

### 8. Configurar Nginx (Recomendado)

Ejemplo de configuración de Nginx:

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location /static/ {
        alias /ruta/al/proyecto/staticfiles/;
    }

    location /media/ {
        alias /ruta/al/proyecto/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 9. Configurar SSL con Let's Encrypt (Recomendado)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com
```

## 📊 Uso del Sistema

### Flujo de Trabajo

1. **Estudiante crea proyecto**:
   - Inicia sesión
   - Crea un nuevo proyecto con título, descripción y archivo PDF
   - El proyecto se crea con estado "Enviado"

2. **Docente revisa proyecto**:
   - Accede al dashboard y ve todos los proyectos
   - Cambia el estado a "En Revisión"
   - Agrega comentarios con retroalimentación
   - El estudiante recibe notificación por email

3. **Estudiante responde**:
   - Recibe email de notificación
   - Lee los comentarios del docente
   - Puede editar el proyecto si estado != "Aprobado"
   - Puede agregar comentarios de respuesta

4. **Docente aprueba proyecto**:
   - Asigna calificación (0.0 - 5.0)
   - Cambia estado a "Aprobado"
   - El proyecto queda bloqueado (no se puede editar ni comentar)

### Estados de Proyecto

- **Enviado**: Estado inicial, estudiante puede editar/eliminar
- **En Revisión**: Docente está revisando, estudiante no puede editar/eliminar
- **Aprobado**: Estado final, nadie puede editar, no se permiten más comentarios

### Exportación de Reportes

Los docentes pueden exportar reportes en dos formatos:

- **CSV**: Archivo de valores separados por comas para análisis en Excel
- **PDF**: Documento con encabezado institucional y tabla de proyectos

## 🧪 Testing

Para ejecutar las pruebas:

```bash
python manage.py test
```

## 🐛 Solución de Problemas

### Error: "No module named 'crispy_forms'"

```bash
pip install django-crispy-forms crispy-tailwind
```

### Error: "No module named 'reportlab'"

```bash
pip install reportlab
```

### Error: "No module named 'dotenv'"

```bash
pip install python-dotenv
```

### Error: "relation 'auth_group' does not exist"

```bash
python manage.py migrate
```

### Error: "could not translate host name to address" o "connection refused" (PostgreSQL)

Este error ocurre cuando Django intenta conectarse a PostgreSQL pero no está disponible.

**Solución para desarrollo (usar SQLite)**:
1. Elimine o renombre el archivo `.env`: `Move-Item .env .env.backup`
2. O edite `.env` y elimine/comente las variables `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`
3. Reinicie el servidor: `python manage.py runserver`

**Solución para producción (configurar PostgreSQL)**:
1. Verifique que PostgreSQL esté instalado y ejecutándose
2. Verifique las credenciales en `.env`
3. Verifique que el host sea accesible

### Error: "CSRF verification failed"

Asegúrese de que `CSRF_TRUSTED_ORIGINS` en `.env` incluye su dominio con `https://`:

```env
CSRF_TRUSTED_ORIGINS=https://tu-dominio.com
```

### Los emails no se envían

**Desarrollo**: Los emails se muestran en la consola por defecto.

**Producción**: Configure las variables de entorno de SMTP:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-password-de-aplicacion
```

## 📝 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 👨‍💻 Autor

Desarrollado como proyecto académico para la gestión de trabajos estudiantiles.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Cree una rama para su feature (`git checkout -b feature/AmazingFeature`)
3. Commit sus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abra un Pull Request

## 📞 Soporte

Para reportar problemas o solicitar características, abra un issue en el repositorio.

---

**Nota**: Este README asume que está usando el nombre de proyecto `proyecto_fernando`. Ajuste los nombres según su configuración específica.
