#!/usr/bin/env python3
"""
Script de inicialización de base de datos para módulo de Recursos Humanos
Crea tablas: posiciones y empleados
"""

import os
import sys
from db_config import get_db_connection, release_db_connection

def init_rrhh_tables():
    """Inicializar tablas de Recursos Humanos"""
    conn = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("🔧 Iniciando creación de tablas de Recursos Humanos...")
        
        # Tabla de posiciones de trabajo
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posiciones (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(255) UNIQUE NOT NULL,
                premio_toyota DECIMAL(10, 2) DEFAULT 0,
                activo BOOLEAN DEFAULT TRUE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ Tabla 'posiciones' creada")
        
        # Tabla de empleados
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS empleados (
                id SERIAL PRIMARY KEY,
                legajo VARCHAR(50) UNIQUE NOT NULL,
                nombre_completo VARCHAR(255) NOT NULL,
                posicion_id INTEGER REFERENCES posiciones(id) ON DELETE SET NULL,
                fecha_alta DATE DEFAULT CURRENT_DATE,
                fecha_baja DATE,
                activo BOOLEAN DEFAULT TRUE,
                observaciones TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ Tabla 'empleados' creada")
        
        # Índices para mejorar rendimiento
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_empleados_posicion 
            ON empleados(posicion_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_empleados_activo 
            ON empleados(activo)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_posiciones_activo 
            ON posiciones(activo)
        ''')
        
        print("✅ Índices creados")
        
        # Insertar posiciones de ejemplo (opcional)
        cursor.execute('''
            INSERT INTO posiciones (nombre, premio_toyota) 
            VALUES 
                ('Gerente General', 150000),
                ('Gerente de Ventas', 100000),
                ('Jefe de Área', 75000),
                ('Vendedor Senior', 50000),
                ('Vendedor', 35000),
                ('Administrativo', 25000),
                ('Recepcionista', 20000)
            ON CONFLICT (nombre) DO NOTHING
        ''')
        
        conn.commit()
        print("✅ Posiciones de ejemplo insertadas")
        
        print("\n✅ ¡Tablas de Recursos Humanos creadas exitosamente!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error al crear tablas: {e}")
        if conn:
            conn.rollback()
        return False
        
    finally:
        if conn:
            release_db_connection(conn)

if __name__ == "__main__":
    print("=" * 60)
    print("INICIALIZACIÓN DE BASE DE DATOS - RECURSOS HUMANOS")
    print("=" * 60)
    
    success = init_rrhh_tables()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ Proceso completado exitosamente")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ Proceso finalizado con errores")
        print("=" * 60)
        sys.exit(1)
