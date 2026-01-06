#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Inicialización de tablas para módulo USADOS
"""

import psycopg2
from db_config import get_db_connection

def create_usados_tables():
    """Crear todas las tablas del módulo Usados"""
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        print("Creando tablas del módulo USADOS...")
        
        # Tabla: Marcas de vehículos usados
        print("- Creando tabla: marcas_usados")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS marcas_usados (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) UNIQUE NOT NULL,
                activo BOOLEAN DEFAULT TRUE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Tabla: Modelos de vehículos usados
        print("- Creando tabla: modelos_usados")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS modelos_usados (
                id SERIAL PRIMARY KEY,
                marca_id INTEGER REFERENCES marcas_usados(id) ON DELETE CASCADE,
                nombre VARCHAR(100) NOT NULL,
                activo BOOLEAN DEFAULT TRUE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(marca_id, nombre)
            );
        """)
        
        # Tabla: Configuración de operaciones de lavado
        print("- Creando tabla: config_operaciones_lavado")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS config_operaciones_lavado (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) UNIQUE NOT NULL,
                duracion_minutos INTEGER NOT NULL,
                es_sistema BOOLEAN DEFAULT FALSE,
                activo BOOLEAN DEFAULT TRUE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Insertar operaciones por defecto
        print("- Insertando operaciones de lavado por defecto...")
        cur.execute("""
            INSERT INTO config_operaciones_lavado (nombre, duracion_minutos, es_sistema, activo)
            VALUES 
                ('Standard', 40, TRUE, TRUE),
                ('Standard Plus', 50, TRUE, TRUE),
                ('Standard Light', 30, TRUE, TRUE),
                ('Repaso', 10, TRUE, TRUE),
                ('Entrega', 20, TRUE, TRUE)
            ON CONFLICT (nombre) DO NOTHING;
        """)
        
        # Tabla: Ingresos de vehículos usados
        print("- Creando tabla: ingresos_usados")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ingresos_usados (
                id SERIAL PRIMARY KEY,
                dominio VARCHAR(20) UNIQUE NOT NULL,
                marca_id INTEGER REFERENCES marcas_usados(id),
                modelo_id INTEGER REFERENCES modelos_usados(id),
                limpieza_requerida VARCHAR(50) NOT NULL,
                fecha_ingreso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Estados y tiempos
                estado VARCHAR(50) DEFAULT 'Playa Lavadero',
                fecha_programacion TIMESTAMP,
                fecha_inicio_lavado TIMESTAMP,
                fecha_fin_lavado TIMESTAMP,
                
                -- Metadata
                usuario_ingreso VARCHAR(100),
                observaciones TEXT,
                activo BOOLEAN DEFAULT TRUE
            );
        """)
        
        # Tabla: Planificación de operaciones (Gantt)
        print("- Creando tabla: planificacion_operaciones")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS planificacion_operaciones (
                id SERIAL PRIMARY KEY,
                ingreso_id INTEGER REFERENCES ingresos_usados(id) ON DELETE CASCADE,
                operacion_lavado_id INTEGER REFERENCES config_operaciones_lavado(id),
                
                -- Planificación
                fecha_planificada TIMESTAMP NOT NULL,
                hora_inicio TIME NOT NULL,
                hora_fin TIME NOT NULL,
                posicion_lavadero INTEGER CHECK (posicion_lavadero IN (1, 2)),
                orden_ejecucion INTEGER,
                
                -- Estado
                estado VARCHAR(50) DEFAULT 'Programado',
                completado BOOLEAN DEFAULT FALSE,
                fecha_completado TIMESTAMP,
                
                -- Tiempos reales
                tiempo_inicio_real TIMESTAMP,
                tiempo_fin_real TIMESTAMP,
                
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Tabla: Historial de estados (para tracking de tiempos)
        print("- Creando tabla: historial_estados_usados")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS historial_estados_usados (
                id SERIAL PRIMARY KEY,
                ingreso_id INTEGER REFERENCES ingresos_usados(id) ON DELETE CASCADE,
                estado_anterior VARCHAR(50),
                estado_nuevo VARCHAR(50) NOT NULL,
                fecha_cambio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usuario VARCHAR(100),
                observaciones TEXT
            );
        """)
        
        # Tabla: Configuración de turnos de trabajo
        print("- Creando tabla: turnos_lavadero")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS turnos_lavadero (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(50) NOT NULL,
                dia_semana INTEGER CHECK (dia_semana BETWEEN 0 AND 6),
                hora_inicio TIME NOT NULL,
                hora_fin TIME NOT NULL,
                activo BOOLEAN DEFAULT TRUE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Insertar turno por defecto (Lunes a Viernes, 8:00 a 18:00)
        print("- Insertando turnos por defecto...")
        for dia in range(5):  # 0=Lunes, 4=Viernes
            cur.execute("""
                INSERT INTO turnos_lavadero (nombre, dia_semana, hora_inicio, hora_fin, activo)
                VALUES (%s, %s, %s, %s, TRUE)
                ON CONFLICT DO NOTHING;
            """, (f"Turno Normal - Día {dia+1}", dia, '08:00', '18:00'))
        
        # Tabla: Reservas KINTO (autos de alquiler)
        print("- Creando tabla: reservas_kinto")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS reservas_kinto (
                id SERIAL PRIMARY KEY,
                fecha_reserva DATE NOT NULL,
                hora_inicio TIME NOT NULL,
                hora_fin TIME NOT NULL,
                dominio VARCHAR(20) NOT NULL,
                duracion_minutos INTEGER DEFAULT 50,
                observaciones TEXT,
                estado VARCHAR(20) DEFAULT 'Reservado',
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usuario VARCHAR(100),
                planificacion_id INTEGER REFERENCES planificacion_operaciones(id) ON DELETE SET NULL
            );
        """)
        
        # Crear índices
        print("- Creando índices...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_ingresos_dominio ON ingresos_usados(dominio);
            CREATE INDEX IF NOT EXISTS idx_ingresos_estado ON ingresos_usados(estado);
            CREATE INDEX IF NOT EXISTS idx_ingresos_fecha ON ingresos_usados(fecha_ingreso);
            CREATE INDEX IF NOT EXISTS idx_planificacion_fecha ON planificacion_operaciones(fecha_planificada);
            CREATE INDEX IF NOT EXISTS idx_planificacion_estado ON planificacion_operaciones(estado);
            CREATE INDEX IF NOT EXISTS idx_historial_ingreso ON historial_estados_usados(ingreso_id);
            CREATE INDEX IF NOT EXISTS idx_kinto_fecha ON reservas_kinto(fecha_reserva);
            CREATE INDEX IF NOT EXISTS idx_kinto_dominio ON reservas_kinto(dominio);
        """)
        
        conn.commit()
        print("\n✓ Todas las tablas del módulo USADOS creadas exitosamente")
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ Error al crear tablas: {e}")
        raise
    
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("INICIALIZACIÓN MÓDULO USADOS")
    print("=" * 60)
    create_usados_tables()
