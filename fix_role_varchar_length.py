"""
Script para aumentar el límite de caracteres en la columna 'role' de la tabla users
De VARCHAR(20) a VARCHAR(50) para soportar 'usuario_plus_plus_plus'
"""

from db_config import get_db_connection, release_db_connection

def fix_role_varchar_length():
    """Aumentar límite de caracteres en columna role"""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        print("🔄 Modificando columna 'role' en tabla users...")
        
        # Aumentar el límite de VARCHAR(20) a VARCHAR(50)
        cur.execute("""
            ALTER TABLE users 
            ALTER COLUMN role TYPE VARCHAR(50)
        """)
        
        conn.commit()
        print("✅ Columna 'role' actualizada exitosamente a VARCHAR(50)")
        print("   Ahora se pueden usar roles largos como 'usuario_plus_plus_plus'")
        
        cur.close()
        release_db_connection(conn)
        
    except Exception as e:
        if conn:
            conn.rollback()
            release_db_connection(conn)
        print(f"❌ Error: {e}")
        raise

if __name__ == '__main__':
    print("🚀 Iniciando migración de base de datos...")
    fix_role_varchar_length()
    print("✅ Migración completada")
