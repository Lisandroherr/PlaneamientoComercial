"""
Script para crear la tabla de planes de crédito en la base de datos.
Esta tabla almacenará los diferentes planes de financiación con sus plazos, tasas y quebrantos.
"""

import psycopg2
from db_config import get_db_connection, release_db_connection

def crear_tabla_planes_credito():
    """Crear tabla planes_credito en la base de datos"""
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Crear tabla planes_credito
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS planes_credito (
                id SERIAL PRIMARY KEY,
                nombre_plan VARCHAR(200) NOT NULL UNIQUE,
                importe_maximo NUMERIC(15, 2) DEFAULT 0,
                plazos JSONB NOT NULL,
                tasas JSONB NOT NULL,
                quebrantos JSONB NOT NULL,
                activo BOOLEAN DEFAULT TRUE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        
        # Agregar columna si no existe (para bases de datos existentes)
        cursor.execute("""
            ALTER TABLE planes_credito 
            ADD COLUMN IF NOT EXISTS importe_maximo NUMERIC(15, 2) DEFAULT 0
        """)
        
        conn.commit()
        print("✅ Tabla 'planes_credito' creada exitosamente")
        
        # Insertar un plan de ejemplo
        cursor.execute("""
            INSERT INTO planes_credito (nombre_plan, importe_maximo, plazos, tasas, quebrantos)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (nombre_plan) DO NOTHING
        """, (
            'Plan Estándar',
            10000000,
            '{"12": true, "24": true, "36": true}',
            '{"12": 15.5, "24": 18.0, "36": 20.5}',
            '{"12": 5.0, "24": 7.5, "36": 10.0}'
        ))
        
        conn.commit()
        print("✅ Plan de crédito de ejemplo insertado")
        
    except psycopg2.Error as e:
        print(f"❌ Error al crear la tabla: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)

if __name__ == '__main__':
    crear_tabla_planes_credito()
