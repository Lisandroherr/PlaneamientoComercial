"""
Script para agregar columna hora_pactada_registro a pv_historial
Esto permite distinguir:
- hora_atender: cuando se presiona "Atender"
- hora_pactada_registro: cuando se presiona "Pactar Hora" (momento de registro)
- hora_pactada: la fecha/hora acordada con el cliente para entregar
- hora_entregado: cuando se presiona "Entregar"

Tiempos calculados:
- Tiempo de atención = hora_pactada_registro - hora_atender
- Tiempo de ejecución = hora_entregado - hora_pactada_registro  
- Tiempo total = hora_entregado - hora_atender
"""

from db_config import get_db_connection as get_pg_connection, release_db_connection

def main():
    conn = None
    try:
        conn = get_pg_connection()
        cur = conn.cursor()
        
        # Verificar si la columna ya existe
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='pv_historial' AND column_name='hora_pactada_registro'
        """)
        
        if cur.fetchone():
            print("La columna hora_pactada_registro ya existe")
        else:
            print("Agregando columna hora_pactada_registro...")
            cur.execute("""
                ALTER TABLE pv_historial 
                ADD COLUMN hora_pactada_registro TIMESTAMP
            """)
            print("✅ Columna agregada exitosamente")
        
        # Agregar columnas de tiempo calculado
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='pv_historial' AND column_name='tiempo_atencion_minutos'
        """)
        
        if cur.fetchone():
            print("La columna tiempo_atencion_minutos ya existe")
        else:
            print("Agregando columna tiempo_atencion_minutos...")
            cur.execute("""
                ALTER TABLE pv_historial 
                ADD COLUMN tiempo_atencion_minutos INTEGER
            """)
            print("✅ Columna tiempo_atencion_minutos agregada")
        
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='pv_historial' AND column_name='tiempo_ejecucion_minutos'
        """)
        
        if cur.fetchone():
            print("La columna tiempo_ejecucion_minutos ya existe")
        else:
            print("Agregando columna tiempo_ejecucion_minutos...")
            cur.execute("""
                ALTER TABLE pv_historial 
                ADD COLUMN tiempo_ejecucion_minutos INTEGER
            """)
            print("✅ Columna tiempo_ejecucion_minutos agregada")
        
        conn.commit()
        cur.close()
        release_db_connection(conn)
        
        print("\n✅ Migración completada exitosamente")
        print("\nAhora se podrá calcular:")
        print("  - Tiempo de atención (desde Atender hasta Pactar Hora)")
        print("  - Tiempo de ejecución (desde Pactar Hora hasta Entregar)")
        print("  - Tiempo total (desde Atender hasta Entregar)")
        
    except Exception as e:
        if conn:
            conn.rollback()
            release_db_connection(conn)
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
