"""
Script para verificar la configuración de servicios con asesores fijos
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def verificar_servicios():
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL no configurada")
            
        conn = psycopg2.connect(database_url)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🔍 Verificando configuración de servicios...")
        
        # Ver servicios con asesor fijo
        cur.execute("""
            SELECT s.id, s.nombre, s.sector, s.asesor_fijo_id, a.nombre as asesor_nombre
            FROM pv_servicios s
            LEFT JOIN pv_asesores a ON s.asesor_fijo_id = a.id
            WHERE s.activo = TRUE AND s.asesor_fijo_id IS NOT NULL
            ORDER BY s.sector, s.nombre
        """)
        
        servicios = cur.fetchall()
        
        if servicios:
            print(f"\n✅ {len(servicios)} servicios con asesor fijo asignado:\n")
            
            sector_actual = None
            for s in servicios:
                if s['sector'] != sector_actual:
                    sector_actual = s['sector']
                    print(f"\n📋 {sector_actual}:")
                
                print(f"  • {s['nombre']} → {s['asesor_nombre']} (ID: {s['asesor_fijo_id']})")
        else:
            print("\n⚠️ No hay servicios con asesor fijo asignado")
        
        # Verificar asesores activos
        print("\n" + "=" * 60)
        print("👥 Asesores activos:")
        cur.execute("""
            SELECT id, nombre, sector, activo
            FROM pv_asesores
            ORDER BY sector, nombre
        """)
        
        asesores = cur.fetchall()
        sector_actual = None
        for a in asesores:
            if a['sector'] != sector_actual:
                sector_actual = a['sector']
                print(f"\n{sector_actual}:")
            
            estado = "✅ Activo" if a['activo'] else "❌ Inactivo"
            print(f"  • {a['nombre']} (ID: {a['id']}) - {estado}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("VERIFICAR CONFIGURACIÓN DE SERVICIOS")
    print("=" * 60)
    verificar_servicios()
