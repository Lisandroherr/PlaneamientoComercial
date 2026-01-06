"""
Script para agregar columnas de retiro a las tablas pv_turnos y pv_historial
"""
import psycopg2
from db_config import get_db_connection, release_db_connection

def add_retiro_columns():
    conn = None
    
    try:
        print("Conectando a la base de datos...")
        conn = get_db_connection()
        cur = conn.cursor()
        
        print("\n=== Agregando columnas a pv_turnos ===")
        
        # Verificar si ya existen las columnas
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'pv_turnos' 
            AND column_name IN ('hora_retiro_inicio', 'hora_atender_retiro', 'fecha_registro')
        """)
        existing_columns = [row['column_name'] for row in cur.fetchall()]
        
        if 'hora_retiro_inicio' not in existing_columns:
            print("Agregando columna hora_retiro_inicio...")
            cur.execute("""
                ALTER TABLE pv_turnos 
                ADD COLUMN hora_retiro_inicio TIMESTAMP
            """)
            print("✓ Columna hora_retiro_inicio agregada")
        else:
            print("✓ Columna hora_retiro_inicio ya existe")
        
        if 'hora_atender_retiro' not in existing_columns:
            print("Agregando columna hora_atender_retiro...")
            cur.execute("""
                ALTER TABLE pv_turnos 
                ADD COLUMN hora_atender_retiro TIMESTAMP
            """)
            print("✓ Columna hora_atender_retiro agregada")
        else:
            print("✓ Columna hora_atender_retiro ya existe")
        
        if 'fecha_registro' not in existing_columns:
            print("Agregando columna fecha_registro (timestamp de asignación)...")
            cur.execute("""
                ALTER TABLE pv_turnos 
                ADD COLUMN fecha_registro TIMESTAMP
            """)
            print("✓ Columna fecha_registro agregada")
        else:
            print("✓ Columna fecha_registro ya existe")
        
        # Actualizar el CHECK constraint de estado para incluir nuevos estados
        print("\nActualizando constraint de estado...")
        cur.execute("""
            ALTER TABLE pv_turnos 
            DROP CONSTRAINT IF EXISTS pv_turnos_estado_check
        """)
        cur.execute("""
            ALTER TABLE pv_turnos 
            ADD CONSTRAINT pv_turnos_estado_check 
            CHECK (estado IN ('Asignado', 'En Atención', 'Hora Pactada', 'Esperando Retiro', 'Listo para Entrega', 'Entregado', 'Cancelado'))
        """)
        print("✓ Constraint de estado actualizado")
        
        print("\n=== Agregando columnas a pv_historial ===")
        
        # Verificar columnas en pv_historial
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'pv_historial' 
            AND column_name IN ('hora_retiro_inicio', 'hora_atender_retiro', 'tiempo_espera_egreso_minutos', 'hora_pactada_registro', 'tiempo_atencion_minutos', 'tiempo_ejecucion_minutos')
        """)
        existing_hist_columns = [row['column_name'] for row in cur.fetchall()]
        
        if 'hora_retiro_inicio' not in existing_hist_columns:
            print("Agregando columna hora_retiro_inicio...")
            cur.execute("""
                ALTER TABLE pv_historial 
                ADD COLUMN hora_retiro_inicio TIMESTAMP
            """)
            print("✓ Columna hora_retiro_inicio agregada")
        else:
            print("✓ Columna hora_retiro_inicio ya existe")
        
        if 'hora_atender_retiro' not in existing_hist_columns:
            print("Agregando columna hora_atender_retiro...")
            cur.execute("""
                ALTER TABLE pv_historial 
                ADD COLUMN hora_atender_retiro TIMESTAMP
            """)
            print("✓ Columna hora_atender_retiro agregada")
        else:
            print("✓ Columna hora_atender_retiro ya existe")
        
        if 'tiempo_espera_egreso_minutos' not in existing_hist_columns:
            print("Agregando columna tiempo_espera_egreso_minutos...")
            cur.execute("""
                ALTER TABLE pv_historial 
                ADD COLUMN tiempo_espera_egreso_minutos NUMERIC(10,2)
            """)
            print("✓ Columna tiempo_espera_egreso_minutos agregada")
        else:
            print("✓ Columna tiempo_espera_egreso_minutos ya existe")
        
        if 'hora_pactada_registro' not in existing_hist_columns:
            print("Agregando columna hora_pactada_registro...")
            cur.execute("""
                ALTER TABLE pv_historial 
                ADD COLUMN hora_pactada_registro TIMESTAMP
            """)
            print("✓ Columna hora_pactada_registro agregada")
        else:
            print("✓ Columna hora_pactada_registro ya existe")
        
        if 'tiempo_atencion_minutos' not in existing_hist_columns:
            print("Agregando columna tiempo_atencion_minutos...")
            cur.execute("""
                ALTER TABLE pv_historial 
                ADD COLUMN tiempo_atencion_minutos NUMERIC(10,2)
            """)
            print("✓ Columna tiempo_atencion_minutos agregada")
        else:
            print("✓ Columna tiempo_atencion_minutos ya existe")
        
        if 'tiempo_ejecucion_minutos' not in existing_hist_columns:
            print("Agregando columna tiempo_ejecucion_minutos...")
            cur.execute("""
                ALTER TABLE pv_historial 
                ADD COLUMN tiempo_ejecucion_minutos NUMERIC(10,2)
            """)
            print("✓ Columna tiempo_ejecucion_minutos agregada")
        else:
            print("✓ Columna tiempo_ejecucion_minutos ya existe")
        
        conn.commit()
        print("\n✅ TODAS LAS COLUMNAS HAN SIDO AGREGADAS EXITOSAMENTE")
        
        cur.close()
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"\n❌ ERROR: {e}")
        raise
    finally:
        if conn:
            release_db_connection(conn)
            print("\nConexión devuelta al pool")

if __name__ == '__main__':
    add_retiro_columns()
