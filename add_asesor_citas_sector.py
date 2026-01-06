import psycopg2
from db_config import get_db_connection

def add_asesor_citas_sector():
    """Agregar 'Asesor de citas' como opción válida en el sector de asesores"""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        print("Modificando constraint de sector en pv_asesores...")
        
        # Eliminar el constraint anterior
        cur.execute("""
            ALTER TABLE pv_asesores 
            DROP CONSTRAINT IF EXISTS pv_asesores_sector_check
        """)
        
        # Agregar el nuevo constraint con 'Asesor de citas'
        cur.execute("""
            ALTER TABLE pv_asesores 
            ADD CONSTRAINT pv_asesores_sector_check 
            CHECK (sector IN ('Servicios', 'Chapería y Pintura', 'Asesor de citas'))
        """)
        
        conn.commit()
        print("✅ Constraint actualizado exitosamente")
        print("Ahora se puede crear asesores con sector 'Asesor de citas'")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        if conn:
            conn.rollback()
            conn.close()
        print(f"❌ Error: {e}")
        raise

if __name__ == '__main__':
    add_asesor_citas_sector()
