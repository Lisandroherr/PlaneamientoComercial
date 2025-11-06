"""
Script para crear la tabla de usuarios en PostgreSQL
Este script debe ejecutarse una sola vez para inicializar la tabla users
"""

import os
from dotenv import load_dotenv
import psycopg2
from werkzeug.security import generate_password_hash

# Cargar variables de entorno
load_dotenv()

def init_users_table():
    """Crear tabla de usuarios en PostgreSQL"""
    
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL no está configurada")
        return
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Crear tabla users si no existe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'user',
                full_name VARCHAR(200),
                email VARCHAR(200),
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Crear índices para mejorar rendimiento
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)
        ''')
        
        conn.commit()
        print("✅ Tabla 'users' creada exitosamente")
        
        # Verificar si existe algún usuario
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Crear usuario admin inicial desde variables de entorno
            admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            admin_email = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
            
            password_hash = generate_password_hash(admin_password)
            
            cursor.execute('''
                INSERT INTO users (username, password_hash, role, full_name, email)
                VALUES (%s, %s, %s, %s, %s)
            ''', (admin_username, password_hash, 'admin', 'Administrador', admin_email))
            
            conn.commit()
            print(f"✅ Usuario administrador creado: {admin_username}")
            print(f"⚠️  IMPORTANTE: Cambiar la contraseña después del primer login")
        else:
            print(f"ℹ️  Ya existen {count} usuario(s) en la base de datos")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error al crear tabla users: {e}")
        raise

if __name__ == '__main__':
    print("🔄 Inicializando tabla de usuarios...")
    init_users_table()
    print("✅ Proceso completado")
