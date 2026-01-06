#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Migración: Agregar campo tasa_inflacion_mensual a planes_credito
"""

import psycopg2
from db_config import get_db_connection

def add_tasa_inflacion_field():
    """Agregar campo tasa_inflacion_mensual a la tabla planes_credito"""
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Agregar columna tasa_inflacion_mensual (porcentaje, ej: 4.0 para 4%)
        # Solo aplica para créditos UVA
        print("Agregando campo tasa_inflacion_mensual...")
        cur.execute("""
            ALTER TABLE planes_credito 
            ADD COLUMN IF NOT EXISTS tasa_inflacion_mensual DECIMAL(5,2) DEFAULT 4.0;
        """)
        
        print("Campo agregado exitosamente")
        
        # Crear índice para mejor performance
        print("Creando índice...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_planes_credito_inflacion 
            ON planes_credito(tasa_inflacion_mensual);
        """)
        
        print("Índice creado")
        
        conn.commit()
        print("\n✓ Migración completada exitosamente")
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ Error en la migración: {e}")
        raise
    
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("MIGRACIÓN: Agregar tasa_inflacion_mensual")
    print("=" * 60)
    add_tasa_inflacion_field()
