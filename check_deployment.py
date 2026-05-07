#!/usr/bin/env python3
"""
Script para verificar el estado del despliegue en DocPloy
"""
import os
import sys
import django
import time
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_fernando.settings')
django.setup()

from django.conf import settings
from django.db import connection
from django.contrib.auth.models import User, Group

def check_database():
    """Verifica la conexión a la base de datos"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        print("✅ Conexión a base de datos: OK")
        
        # Verificar tipo de base de datos
        db_engine = settings.DATABASES['default']['ENGINE']
        if 'sqlite' in db_engine:
            print("⚠️  Usando SQLite")
        else:
            print(f"✅ Usando: {db_engine}")
            
        return True
    except Exception as e:
        print(f"❌ Error de base de datos: {e}")
        return False

def check_users_groups():
    """Verifica usuarios y grupos"""
    try:
        # Verificar grupos
        estudiante_group = Group.objects.filter(name='estudiante').exists()
        docente_group = Group.objects.filter(name='docente').exists()
        
        print(f"✅ Grupo estudiante: {'OK' if estudiante_group else 'FALTA'}")
        print(f"✅ Grupo docente: {'OK' if docente_group else 'FALTA'}")
        
        # Verificar superusuario
        superuser_exists = User.objects.filter(is_superuser=True).exists()
        print(f"✅ Superusuario: {'OK' if superuser_exists else 'FALTA'}")
        
        # Verificar usuarios de prueba
        docente_exists = User.objects.filter(username='docente').exists()
        estudiante_exists = User.objects.filter(username='estudiante').exists()
        
        print(f"✅ Usuario docente: {'OK' if docente_exists else 'FALTA'}")
        print(f"✅ Usuario estudiante: {'OK' if estudiante_exists else 'FALTA'}")
        
        return True
    except Exception as e:
        print(f"❌ Error verificando usuarios: {e}")
        return False

def check_static_files():
    """Verifica archivos estáticos"""
    try:
        static_root = Path(settings.STATIC_ROOT)
        if static_root.exists():
            file_count = len(list(static_root.rglob('*')))
            print(f"✅ Archivos estáticos: {file_count} archivos")
        else:
            print("❌ Directorio de archivos estáticos no existe")
            return False
        return True
    except Exception as e:
        print(f"❌ Error verificando archivos estáticos: {e}")
        return False

def check_media_files():
    """Verifica configuración de archivos media"""
    try:
        media_root = Path(settings.MEDIA_ROOT)
        if media_root.exists():
            print("✅ Directorio media: OK")
        else:
            print("⚠️  Directorio media no existe (se creará automáticamente)")
        return True
    except Exception as e:
        print(f"❌ Error verificando archivos media: {e}")
        return False

def main():
    print("🔍 Verificando estado del despliegue...")
    print("=" * 50)
    
    checks = [
        ("Base de datos", check_database),
        ("Usuarios y grupos", check_users_groups),
        ("Archivos estáticos", check_static_files),
        ("Archivos media", check_media_files),
    ]
    
    all_passed = True
    
    for name, check_func in checks:
        print(f"\n📋 {name}:")
        try:
            result = check_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ Error en {name}: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ Todas las verificaciones pasaron")
        print("🚀 El sistema debería estar funcionando correctamente")
    else:
        print("❌ Algunas verificaciones fallaron")
        print("🔧 Revise los errores arriba")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())