"""
Script para agregar la columna servicio_id a pv_turnos
Esto permite una asignación más confiable usando el ID del servicio
en lugar de solo el nombre.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def add_servicio_id_column():
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL no configurada")
            
        conn = psycopg2.connect(database_url)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🔧 Verificando estructura de pv_turnos...")
        
        # Verificar si la columna ya existe
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'pv_turnos' AND column_name = 'servicio_id'
        """)
        
        if cur.fetchone():
            print("✅ La columna servicio_id ya existe en pv_turnos")
        else:
            print("➕ Agregando columna servicio_id a pv_turnos...")
            
            # Agregar la columna servicio_id con FK a pv_servicios
            cur.execute("""
                ALTER TABLE pv_turnos 
                ADD COLUMN servicio_id INTEGER REFERENCES pv_servicios(id)
            """)
            
            print("✅ Columna servicio_id agregada exitosamente")
            
            # Intentar poblar los servicio_id existentes basándose en el servicio_nombre
            print("🔄 Actualizando registros existentes...")
            cur.execute("""
                UPDATE pv_turnos t
                SET servicio_id = s.id
                FROM pv_servicios s
                WHERE t.servicio_nombre = s.nombre
                AND t.servicio_id IS NULL
            """)
            
            rows_updated = cur.rowcount
            print(f"✅ {rows_updated} registros actualizados con servicio_id")
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("\n✅ Migración completada exitosamente")
        
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("MIGRACIÓN: Agregar servicio_id a pv_turnos")
    print("=" * 60)
    add_servicio_id_column()
