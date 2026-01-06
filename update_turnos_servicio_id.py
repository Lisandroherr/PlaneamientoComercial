"""
Script para actualizar los servicio_id de los turnos existentes
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def update_servicio_ids():
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL no configurada")
            
        conn = psycopg2.connect(database_url)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🔄 Actualizando servicio_id en turnos existentes...")
        
        # Actualizar servicio_id basándose en servicio_nombre
        cur.execute("""
            UPDATE pv_turnos t
            SET servicio_id = s.id
            FROM pv_servicios s
            WHERE t.servicio_nombre = s.nombre
            AND (t.servicio_id IS NULL OR t.servicio_id != s.id)
        """)
        
        rows_updated = cur.rowcount
        print(f"✅ {rows_updated} registros actualizados")
        
        # Verificar turnos sin servicio_id
        cur.execute("""
            SELECT COUNT(*) as total
            FROM pv_turnos
            WHERE servicio_id IS NULL
        """)
        
        result = cur.fetchone()
        sin_servicio = result['total'] if result else 0
        
        if sin_servicio > 0:
            print(f"⚠️ {sin_servicio} turnos sin servicio_id (servicios no encontrados)")
            
            # Mostrar algunos ejemplos
            cur.execute("""
                SELECT id, servicio_nombre
                FROM pv_turnos
                WHERE servicio_id IS NULL
                LIMIT 5
            """)
            
            print("\nEjemplos de servicios no encontrados:")
            for row in cur.fetchall():
                print(f"  - Turno ID {row['id']}: '{row['servicio_nombre']}'")
        else:
            print("✅ Todos los turnos tienen servicio_id asignado")
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("\n✅ Actualización completada")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("ACTUALIZAR servicio_id en pv_turnos")
    print("=" * 60)
    update_servicio_ids()
