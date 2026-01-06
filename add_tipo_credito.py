#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para agregar el campo tipo_credito a la tabla planes_credito
"""

import psycopg2
from psycopg2 import sql
from db_config import get_db_connection, release_db_connection

def add_tipo_credito_column():
    """Agregar columna tipo_credito a la tabla planes_credito"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Agregar columna tipo_credito si no existe
        print("Agregando columna tipo_credito...")
        cursor.execute("""
            ALTER TABLE planes_credito 
            ADD COLUMN IF NOT EXISTS tipo_credito VARCHAR(10) DEFAULT 'pesos';
        """)
        
        # Crear índice para búsquedas por tipo
        print("Creando índice para tipo_credito...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_planes_credito_tipo 
            ON planes_credito(tipo_credito);
        """)
        
        conn.commit()
        print("✓ Campo tipo_credito agregado exitosamente")
        print("  - Valores permitidos: 'pesos', 'uva'")
        print("  - Default: 'pesos'")
        
        cursor.close()
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"✗ Error al agregar campo tipo_credito: {e}")
        raise
    finally:
        if conn:
            release_db_connection(conn)

if __name__ == "__main__":
    print("=" * 60)
    print("AGREGANDO CAMPO TIPO_CREDITO A TABLA planes_credito")
    print("=" * 60)
    add_tipo_credito_column()
    print("=" * 60)
    print("Script completado")
