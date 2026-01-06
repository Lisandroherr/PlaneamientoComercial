#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear tabla de configuración de jornadas laborales
"""

import os
import psycopg2
from psycopg2 import extras
from dotenv import load_dotenv
import sys

# Cargar variables de entorno
load_dotenv()

def crear_tabla_jornadas():
    """Crear tabla para configurar días con jornada corrida"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise ValueError("DATABASE_URL no configurada")
        
        conn = psycopg2.connect(database_url, cursor_factory=extras.RealDictCursor)
        cursor = conn.cursor()
        
        print("🔧 Creando tabla config_jornadas_lavadero...")
        
        # Tabla de configuración de jornadas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config_jornadas_lavadero (
                id SERIAL PRIMARY KEY,
                fecha DATE NOT NULL UNIQUE,
                tipo_jornada VARCHAR(20) NOT NULL DEFAULT 'cortada',
                -- tipo_jornada: 'cortada' (8:30-13:00 y 16:00-20:00) o 'corrida' (8:30-17:30)
                hora_inicio_manana TIME DEFAULT '08:30:00',
                hora_fin_manana TIME DEFAULT '13:00:00',
                hora_inicio_tarde TIME DEFAULT '16:00:00',
                hora_fin_tarde TIME DEFAULT '20:00:00',
                observaciones TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usuario_creacion VARCHAR(100)
            )
        """)
        
        # Índice para búsquedas rápidas por fecha
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_jornadas_fecha 
            ON config_jornadas_lavadero(fecha)
        """)
        
        # Índice para búsquedas por tipo
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_jornadas_tipo 
            ON config_jornadas_lavadero(tipo_jornada)
        """)
        
        conn.commit()
        print("✅ Tabla config_jornadas_lavadero creada exitosamente")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error al crear tabla: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("CONFIGURACIÓN DE JORNADAS LABORALES - LAVADERO")
    print("=" * 60)
    
    if crear_tabla_jornadas():
        print("\n✓ Configuración completada exitosamente")
        sys.exit(0)
    else:
        print("\n✗ Hubo errores en la configuración")
        sys.exit(1)
