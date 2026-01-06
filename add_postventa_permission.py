import psycopg2
from db_config import get_db_connection

def add_postventa_permission():
    """Agregar columna permiso_postventa a la tabla users"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Verificar si la columna ya existe
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='permiso_postventa'
        """)
        
        if cur.fetchone():
            print("✅ La columna permiso_postventa ya existe")
        else:
            # Agregar columna
            cur.execute("""
                ALTER TABLE users 
                ADD COLUMN permiso_postventa BOOLEAN DEFAULT FALSE
            """)
            print("✅ Columna permiso_postventa agregada exitosamente")
        
        conn.commit()
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error al agregar columna: {e}")
        conn.rollback()
        cur.close()
        conn.close()
        raise

if __name__ == '__main__':
    add_postventa_permission()
