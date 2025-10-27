"""
Script para crear tablas de configuración de observaciones
"""

import os
from db_config import get_db_connection, release_db_connection, init_connection_pool

def crear_tablas_observaciones():
    """Crear tablas para sistema de observaciones"""
    
    print("🚀 Creando tablas de observaciones...")
    
    try:
        init_connection_pool()
    except:
        pass
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Tabla de configuración de días por zona
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config_dias_zonas (
                id SERIAL PRIMARY KEY,
                zona INTEGER NOT NULL,
                dias_estandar INTEGER DEFAULT 0,
                dias_desvio INTEGER DEFAULT 0,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(zona)
            )
        ''')
        
        # Tabla de matriz de códigos de observación
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS matriz_codigos_obs (
                id SERIAL PRIMARY KEY,
                clase TEXT NOT NULL,
                zona INTEGER NOT NULL,
                codigos TEXT DEFAULT '',
                es_zona_arribo BOOLEAN DEFAULT FALSE,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(clase, zona)
            )
        ''')
        
        # Tabla de auditoría de cambios de observaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS auditoria_observaciones (
                id SERIAL PRIMARY KEY,
                operacion TEXT NOT NULL,
                codigo_anterior TEXT,
                codigo_nuevo TEXT,
                zona_anterior INTEGER,
                zona_nueva INTEGER,
                ejecutivo TEXT,
                es_retroceso BOOLEAN DEFAULT FALSE,
                fecha_cambio TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de estadísticas por operación
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stats_operaciones (
                id SERIAL PRIMARY KEY,
                operacion TEXT UNIQUE NOT NULL,
                cantidad_cambios INTEGER DEFAULT 0,
                cantidad_retrocesos INTEGER DEFAULT 0,
                marcado_sospechoso BOOLEAN DEFAULT FALSE,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        print("✅ Tablas de observaciones creadas")
        
        # Insertar valores por defecto para días estándar
        cursor.execute('SELECT COUNT(*) as count FROM config_dias_zonas')
        if cursor.fetchone()['count'] == 0:
            dias_default = [
                (1, 5, 2),   # Zona 1: 5 días estándar, 2 días desvío
                (2, 10, 3),  # Zona 2: 10 días estándar, 3 días desvío
                (3, 15, 5),  # Zona 3: 15 días estándar, 5 días desvío
            ]
            
            for zona, dias_est, dias_desv in dias_default:
                cursor.execute('''
                    INSERT INTO config_dias_zonas (zona, dias_estandar, dias_desvio)
                    VALUES (%s, %s, %s)
                ''', (zona, dias_est, dias_desv))
            
            print("✅ Valores por defecto de días insertados")
        
        # Insertar matriz por defecto (ejemplo)
        cursor.execute('SELECT COUNT(*) as count FROM matriz_codigos_obs')
        if cursor.fetchone()['count'] == 0:
            # Matriz por defecto con zonas de arribo correctas por clase
            # IMPORTANTE: Cada clase tiene su propia zona de arribo (zona final del proceso)
            matriz_default = [
                # CLASE A - arribo en zona 4
                ('CLASE A', 1, '1', False),
                ('CLASE A', 2, '1', False),
                ('CLASE A', 3, '0', False),
                ('CLASE A', 4, '3', True),  # Zona de arribo
                # CLASE B - arribo en zona 4
                ('CLASE B', 1, '2,3', False),
                ('CLASE B', 2, '3', False),
                ('CLASE B', 3, '2,3', False),
                ('CLASE B', 4, '4', True),  # Zona de arribo
                # CLASE C - arribo en zona 3
                ('CLASE C', 1, '6,4', False),
                ('CLASE C', 2, '4', False),
                ('CLASE C', 3, '0', True),  # Zona de arribo
                # CLASE D - arribo en zona 2
                ('CLASE D', 1, '5', False),
                ('CLASE D', 2, '0', True),  # Zona de arribo
                # CLASE E - arribo en zona 4
                ('CLASE E', 1, '8,7', False),
                ('CLASE E', 2, '7', False),
                ('CLASE E', 3, '4', False),
                ('CLASE E', 4, '0', True),  # Zona de arribo
            ]
            
            for clase, zona, codigos, es_arribo in matriz_default:
                cursor.execute('''
                    INSERT INTO matriz_codigos_obs (clase, zona, codigos, es_zona_arribo)
                    VALUES (%s, %s, %s, %s)
                ''', (clase, zona, codigos, es_arribo))
            
            print("✅ Matriz de códigos por defecto insertada")
        
        conn.commit()
        release_db_connection(conn)
        
        print("✅ Sistema de observaciones inicializado correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        release_db_connection(conn)
        return False

if __name__ == '__main__':
    crear_tablas_observaciones()
