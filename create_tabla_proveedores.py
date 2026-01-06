"""
Script para crear la tabla de proveedores en el módulo Usados
"""

from db_config import get_db_connection, release_db_connection

def create_proveedores_table():
    """Crear tabla de proveedores para usados"""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        print("🔄 Creando tabla usados_proveedores...")
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usados_proveedores (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(255) NOT NULL,
                cuit VARCHAR(20) NOT NULL UNIQUE,
                rubro VARCHAR(100),
                especialidad VARCHAR(200),
                telefono VARCHAR(50),
                ubicacion VARCHAR(200),
                activo BOOLEAN DEFAULT TRUE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Crear índices
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_proveedores_cuit 
            ON usados_proveedores(cuit)
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_proveedores_rubro 
            ON usados_proveedores(rubro)
        """)
        
        conn.commit()
        print("✅ Tabla usados_proveedores creada exitosamente")
        
        cur.close()
        release_db_connection(conn)
        
    except Exception as e:
        if conn:
            conn.rollback()
            release_db_connection(conn)
        print(f"❌ Error: {e}")
        raise

if __name__ == '__main__':
    print("🚀 Iniciando creación de tabla proveedores...")
    create_proveedores_table()
    print("✅ Proceso completado")
