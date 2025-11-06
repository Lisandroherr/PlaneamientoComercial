"""
Script de ayuda para inicializar el sistema de autenticación
Ejecuta esto después de configurar tu archivo .env
"""

import os
import sys
from dotenv import load_dotenv

def check_environment():
    """Verificar que todas las variables de entorno necesarias estén configuradas"""
    load_dotenv()
    
    required_vars = {
        'DATABASE_URL': 'URL de conexión a PostgreSQL',
        'SECRET_KEY': 'Clave secreta para sesiones',
        'ADMIN_USERNAME': 'Nombre de usuario del admin',
        'ADMIN_PASSWORD': 'Contraseña del admin',
        'ADMIN_EMAIL': 'Email del admin'
    }
    
    missing = []
    for var, description in required_vars.items():
        if not os.environ.get(var):
            missing.append(f"  ❌ {var}: {description}")
        else:
            print(f"  ✅ {var}: Configurado")
    
    if missing:
        print("\n⚠️  Variables de entorno faltantes:")
        for m in missing:
            print(m)
        print("\n📝 Por favor, configura estas variables en tu archivo .env")
        return False
    
    return True

def generate_secret_key():
    """Generar una clave secreta aleatoria"""
    import secrets
    key = secrets.token_hex(32)
    print(f"\n🔑 Clave secreta generada:")
    print(f"SECRET_KEY={key}")
    print("\n💡 Copia esta línea en tu archivo .env")

def initialize_database():
    """Ejecutar el script de inicialización de la base de datos"""
    print("\n🔄 Inicializando base de datos...")
    try:
        import init_users
        init_users.init_users_table()
        return True
    except Exception as e:
        print(f"\n❌ Error al inicializar base de datos: {e}")
        return False

def main():
    print("=" * 60)
    print("🔐 CONFIGURACIÓN DEL SISTEMA DE AUTENTICACIÓN")
    print("=" * 60)
    
    print("\n📋 Paso 1: Verificando variables de entorno...")
    if not check_environment():
        print("\n💡 ¿Necesitas generar una SECRET_KEY? (s/n): ", end="")
        response = input().lower()
        if response == 's':
            generate_secret_key()
        sys.exit(1)
    
    print("\n✅ Todas las variables de entorno están configuradas")
    
    print("\n📋 Paso 2: ¿Inicializar la base de datos? (s/n): ", end="")
    response = input().lower()
    
    if response == 's':
        if initialize_database():
            print("\n✅ Base de datos inicializada correctamente")
            print("\n🎉 ¡Sistema listo para usar!")
            print(f"\n🌐 Puedes iniciar sesión en: http://localhost:7860/login")
            admin_user = os.environ.get('ADMIN_USERNAME', 'admin')
            print(f"   Usuario: {admin_user}")
            print(f"   Contraseña: (la configurada en .env)")
        else:
            print("\n❌ Error en la inicialización")
            sys.exit(1)
    else:
        print("\n⚠️  Recuerda ejecutar 'python init_users.py' antes de usar la app")
    
    print("\n" + "=" * 60)
    print("📖 Para más información, consulta AUTHENTICATION_SETUP.md")
    print("=" * 60)

if __name__ == '__main__':
    main()
