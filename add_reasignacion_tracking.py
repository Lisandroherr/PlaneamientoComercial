"""
Script para agregar columnas de tracking de reasignaciones
"""
from db_config import get_db_connection, release_db_connection

def add_tracking_columns():
    conn = None
    
    try:
        print("Conectando a la base de datos...")
        conn = get_db_connection()
        cur = conn.cursor()
        
        print("\n=== Agregando columnas de tracking a pv_turnos ===")
        
        # Verificar si ya existen las columnas
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'pv_turnos' 
            AND column_name IN ('asesor_original_id', 'fue_reasignado')
        """)
        existing_columns = [row['column_name'] for row in cur.fetchall()]
        
        if 'asesor_original_id' not in existing_columns:
            print("Agregando columna asesor_original_id...")
            cur.execute("""
                ALTER TABLE pv_turnos 
                ADD COLUMN asesor_original_id INTEGER REFERENCES pv_asesores(id)
            """)
            print("✓ Columna asesor_original_id agregada")
        else:
            print("✓ Columna asesor_original_id ya existe")
        
        if 'fue_reasignado' not in existing_columns:
            print("Agregando columna fue_reasignado...")
            cur.execute("""
                ALTER TABLE pv_turnos 
                ADD COLUMN fue_reasignado BOOLEAN DEFAULT FALSE
            """)
            print("✓ Columna fue_reasignado agregada")
        else:
            print("✓ Columna fue_reasignado ya existe")
        
        # Verificar columnas en pv_historial
        print("\n=== Agregando columnas de tracking a pv_historial ===")
        
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'pv_historial' 
            AND column_name IN ('asesor_original_nombre', 'fue_reasignado')
        """)
        existing_hist_columns = [row['column_name'] for row in cur.fetchall()]
        
        if 'asesor_original_nombre' not in existing_hist_columns:
            print("Agregando columna asesor_original_nombre...")
            cur.execute("""
                ALTER TABLE pv_historial 
                ADD COLUMN asesor_original_nombre VARCHAR(100)
            """)
            print("✓ Columna asesor_original_nombre agregada")
        else:
            print("✓ Columna asesor_original_nombre ya existe")
        
        if 'fue_reasignado' not in existing_hist_columns:
            print("Agregando columna fue_reasignado...")
            cur.execute("""
                ALTER TABLE pv_historial 
                ADD COLUMN fue_reasignado BOOLEAN DEFAULT FALSE
            """)
            print("✓ Columna fue_reasignado agregada")
        else:
            print("✓ Columna fue_reasignado ya existe")
        
        conn.commit()
        print("\n✅ TODAS LAS COLUMNAS DE TRACKING HAN SIDO AGREGADAS EXITOSAMENTE")
        
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
    add_tracking_columns()
