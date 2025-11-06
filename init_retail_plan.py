"""
Inicialización de la tabla retail_plan para objetivos del plan de negocio.
Ejecutar una sola vez después de crear la estructura.
"""
import psycopg2
from db_config import get_db_connection

def init_retail_plan_table():
    """Crea la tabla retail_plan si no existe"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Crear tabla
        cur.execute("""
            CREATE TABLE IF NOT EXISTS retail_plan (
                id SERIAL PRIMARY KEY,
                anio INTEGER NOT NULL,
                familia VARCHAR(50) NOT NULL,
                convencional_objetivo INTEGER DEFAULT 0,
                especificas_objetivo INTEGER DEFAULT 0,
                tpa_objetivo INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(anio, familia)
            )
        """)
        
        print("✅ Tabla retail_plan creada exitosamente")
        
        # Insertar datos iniciales para 2025 basados en el Excel del usuario
        familias_iniciales = [
            ('HILUX', 1732, 884, 249, 599),
            ('SW4', 270, 177, 41, 52),
            ('COROLLA', 465, 283, 81, 101),
            ('COROLLA CROSS', 755, 377, 151, 227),
            ('YARIS', 1652, 969, 250, 433),
            ('HIACE', 80, 38, 16, 26),
            ('YARIS CROSS', 0, 0, 0, 0),
            ('RAV 4', 0, 0, 0, 0),
            ('OTROS', 0, 0, 0, 0),
        ]
        
        for familia, pn_total, conv, espec, tpa in familias_iniciales:
            cur.execute("""
                INSERT INTO retail_plan 
                (anio, familia, convencional_objetivo, especificas_objetivo, tpa_objetivo)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (anio, familia) DO NOTHING
            """, (2025, familia, conv, espec, tpa))
        
        print("✅ Datos iniciales cargados para 2025")
        
        conn.commit()
        print("✅ Inicialización completada")
        
    except Exception as e:
        print(f"❌ Error al inicializar tabla retail_plan: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    init_retail_plan_table()
