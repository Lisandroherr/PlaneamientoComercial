"""
Script para actualizar la contraseña del usuario administrador.
Ejecutar cuando cambies la contraseña en las variables de entorno de Render.
"""

import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from db_config import get_db_connection, release_db_connection

# Cargar variables de entorno
load_dotenv()

def update_admin_password():
    """Actualizar la contraseña del administrador desde las variables de entorno"""
    
    admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
    new_password = os.environ.get('ADMIN_PASSWORD')
    
    if not new_password:
        print("❌ Error: No se encontró ADMIN_PASSWORD en las variables de entorno")
        return False
    
    # Conectar a la base de datos
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar si el admin existe
        cursor.execute('SELECT id, username FROM users WHERE username = %s', (admin_username,))
        admin = cursor.fetchone()
        
        if not admin:
            print(f"❌ Error: No se encontró el usuario '{admin_username}' en la base de datos")
            print("   Ejecuta primero: python setup_auth.py")
            release_db_connection(conn)
            return False
        
        # Hashear la nueva contraseña
        hashed_password = generate_password_hash(new_password)
        
        # Actualizar la contraseña
        cursor.execute('''
            UPDATE users 
            SET password_hash = %s
            WHERE username = %s
        ''', (hashed_password, admin_username))
        
        conn.commit()
        release_db_connection(conn)
        
        print("✅ ¡Contraseña actualizada exitosamente!")
        print(f"   Usuario: {admin_username}")
        print(f"   Nueva contraseña: {'*' * len(new_password)}")
        print("\n🔐 La contraseña ha sido hasheada y almacenada de forma segura.")
        print("   Puedes iniciar sesión con la nueva contraseña.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al actualizar la contraseña: {e}")
        if conn:
            conn.rollback()
            release_db_connection(conn)
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("🔐 ACTUALIZACIÓN DE CONTRASEÑA DEL ADMINISTRADOR")
    print("=" * 60)
    print("\nEste script actualizará la contraseña del administrador")
    print("usando el valor de ADMIN_PASSWORD en tu archivo .env\n")
    
    # Si se pasa el argumento --auto, ejecutar sin preguntar
    import sys
    if '--auto' in sys.argv or '-y' in sys.argv:
        update_admin_password()
    else:
        respuesta = input("¿Deseas continuar? (s/n): ")
        
        if respuesta.lower() == 's':
            update_admin_password()
        else:
            print("❌ Operación cancelada")
