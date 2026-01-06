"""Script para agregar campos de clasificación a la tabla ingresos_usados"""

import psycopg2
from db_config import get_db_connection

def agregar_clasificacion():
    conn = None
    try:
        print("Conectando a la base de datos...")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("Agregando columnas clasificacion y es_stock_fijo...")
        
        # Agregar columnas
        cursor.execute("""
            ALTER TABLE ingresos_usados 
            ADD COLUMN IF NOT EXISTS clasificacion VARCHAR(20) DEFAULT 'USADOS',
            ADD COLUMN IF NOT EXISTS es_stock_fijo BOOLEAN DEFAULT FALSE;
        """)
        
        print("Actualizando registros existentes...")
        
        # Actualizar registros existentes
        cursor.execute("""
            UPDATE ingresos_usados 
            SET clasificacion = 'USADOS', es_stock_fijo = FALSE
            WHERE clasificacion IS NULL;
        """)
        
        print("Creando índices...")
        
        # Crear índices
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ingresos_clasificacion ON ingresos_usados(clasificacion);
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ingresos_stock_fijo ON ingresos_usados(es_stock_fijo);
        """)
        
        # Commit
        conn.commit()
        print("✅ Actualización completada exitosamente")
        
        # Verificar
        cursor.execute("""
            SELECT clasificacion, COUNT(*) 
            FROM ingresos_usados 
            WHERE activo = TRUE
            GROUP BY clasificacion
        """)
        
        resultados = cursor.fetchall()
        print("\n📊 Resumen del stock:")
        if resultados:
            for row in resultados:
                print(f"   {row[0] if row else 'NULL'}: {row[1] if len(row) > 1 else 0} vehículos")
        else:
            print("   No hay registros aún")
        
        conn.close()
        
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    agregar_clasificacion()
