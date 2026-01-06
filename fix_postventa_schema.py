import psycopg2
from db_config import get_db_connection

# Drop and recreate tables with correct schema
conn = get_db_connection()
cur = conn.cursor()

try:
    # Drop existing tables
    print("Eliminando tablas existentes...")
    cur.execute("DROP TABLE IF EXISTS pv_historial CASCADE")
    cur.execute("DROP TABLE IF EXISTS pv_turnos CASCADE")
    cur.execute("DROP TABLE IF EXISTS pv_asesores CASCADE")
    cur.execute("DROP TABLE IF EXISTS pv_servicios CASCADE")
    
    # Recreate with correct schema
    print("Creando tablas con esquema correcto...")
    
    # Asesores first (so servicios can reference it)
    cur.execute("""
        CREATE TABLE pv_asesores (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL,
            usuario_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
            sector VARCHAR(50) NOT NULL CHECK (sector IN ('Servicios', 'Chapería y Pintura')),
            activo BOOLEAN DEFAULT TRUE,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Servicios
    cur.execute("""
        CREATE TABLE pv_servicios (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL UNIQUE,
            sector VARCHAR(50) NOT NULL CHECK (sector IN ('Servicios', 'Chapería y Pintura')),
            ranking INTEGER NOT NULL CHECK (ranking >= 1 AND ranking <= 5),
            asesor_fijo_id INTEGER REFERENCES pv_asesores(id) ON DELETE SET NULL,
            activo BOOLEAN DEFAULT TRUE,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Turnos
    cur.execute("""
        CREATE TABLE pv_turnos (
            id SERIAL PRIMARY KEY,
            fecha_turno DATE NOT NULL,
            hora_inicio TIME,
            dominio VARCHAR(20),
            cliente_nombre VARCHAR(255),
            servicio_nombre VARCHAR(255),
            servicio_id INTEGER REFERENCES pv_servicios(id) ON DELETE SET NULL,
            marca_modelo VARCHAR(255),
            sector VARCHAR(50) CHECK (sector IN ('Servicios', 'Chapería y Pintura')),
            asesor_id INTEGER REFERENCES pv_asesores(id) ON DELETE SET NULL,
            estado VARCHAR(50) DEFAULT 'Asignado' CHECK (estado IN ('Asignado', 'En Atención', 'Hora Pactada', 'Entregado', 'Cancelado')),
            fecha_hora_pactada TIMESTAMP,
            hora_atender TIMESTAMP,
            hora_entregado TIMESTAMP,
            observaciones TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Historial
    cur.execute("""
        CREATE TABLE pv_historial (
            id SERIAL PRIMARY KEY,
            turno_id INTEGER UNIQUE REFERENCES pv_turnos(id) ON DELETE CASCADE,
            fecha_turno DATE,
            cliente_nombre VARCHAR(255),
            dominio VARCHAR(20),
            servicio_nombre VARCHAR(255),
            sector VARCHAR(50),
            asesor_nombre VARCHAR(255),
            hora_atender TIMESTAMP,
            hora_pactada TIMESTAMP,
            hora_entregado TIMESTAMP,
            tiempo_total_minutos INTEGER,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert sample services
    print("Insertando servicios...")
    servicios = [
        ('ALINEAR Y BALANCEAR', 'Servicios', 1),
        ('CALADO Y CODIFICADO', 'Servicios', 1),
        ('CAMPAÑA BARRA CON CONTRAMEDIDA', 'Servicios', 1),
        ('CH Y PINT PROPIA', 'Chapería y Pintura', 1),
        ('COLOCACION PARABRISAS', 'Servicios', 1),
        ('CONTACTLESS DE 10.000KM', 'Servicios', 1),
        ('DIAGNOSTICO', 'Servicios', 1),
        ('Diagnóstico', 'Servicios', 1),
        ('DIAGNOSTICO DPF', 'Servicios', 1),
        ('EXPRESS 10.000 KM', 'Servicios', 1),
        ('EXPRESS 30.000 KM', 'Servicios', 1),
        ('EXPRESS 90.000 KM', 'Servicios', 1),
        ('FIR', 'Servicios', 1),
        ('Mantenimiento +150.000', 'Servicios', 1),
        ('Mantenimiento 1.000', 'Servicios', 1),
        ('Mantenimiento 10.000', 'Servicios', 1),
        ('Mantenimiento 100.000', 'Servicios', 1),
        ('Mantenimiento 110.000', 'Servicios', 1),
        ('Mantenimiento 120.000', 'Servicios', 1),
        ('Mantenimiento 130.000', 'Servicios', 1),
        ('Mantenimiento 170.000', 'Servicios', 1),
        ('Mantenimiento 180.000', 'Servicios', 1),
        ('Mantenimiento 20.000', 'Servicios', 1),
        ('Mantenimiento 30.000', 'Servicios', 1),
        ('Mantenimiento 40.000', 'Servicios', 1),
        ('Mantenimiento 50.000', 'Servicios', 1),
        ('Mantenimiento 60.000', 'Servicios', 1),
        ('Mantenimiento 70.000', 'Servicios', 1),
        ('Mantenimiento 80.000', 'Servicios', 1),
        ('Mantenimiento 90.000', 'Servicios', 1),
        ('Mantenimiento Express 10.000', 'Servicios', 1),
        ('Mantenimiento Express 20.000', 'Servicios', 1),
        ('Mantenimiento Express 30.000', 'Servicios', 1),
        ('Mantenimiento Express 40.000', 'Servicios', 1),
        ('Otros', 'Servicios', 1),
        ('PDS - PREPARACIÓN DE PREENTREGA', 'Servicios', 1),
        ('POLARIZADO', 'Servicios', 1),
        ('REP. DE CHAPERIA Y PINTURA', 'Chapería y Pintura', 1),
        ('REP. EN GARANTIA', 'Servicios', 1),
        ('REP. GENERALES', 'Servicios', 1),
        ('Reparación', 'Servicios', 1),
        ('SERVICIO DE 1.000 KM', 'Servicios', 1),
        ('SERVICIO DE 10.000 KM', 'Servicios', 1),
        ('SERVICIO DE 100.000 KM', 'Servicios', 1),
        ('SERVICIO DE 20.000 KM', 'Servicios', 1),
        ('SERVICIO DE 30.000 KM', 'Servicios', 1),
        ('SERVICIO DE 40.000 KM', 'Servicios', 1),
        ('SERVICIO DE 50.000 KM', 'Servicios', 1),
        ('SERVICIO DE 60.000 KM', 'Servicios', 1),
        ('SERVICIO DE 70.000 KM', 'Servicios', 1),
        ('SERVICIO DE 80.000 KM', 'Servicios', 1),
        ('SERVICIO DE 90.000 KM', 'Servicios', 1),
    ]
    
    for nombre, sector, ranking in servicios:
        cur.execute("""
            INSERT INTO pv_servicios (nombre, sector, ranking)
            VALUES (%s, %s, %s)
            ON CONFLICT (nombre) DO UPDATE
            SET sector = EXCLUDED.sector,
                ranking = EXCLUDED.ranking,
                activo = TRUE
        """, (nombre, sector, ranking))
    
    conn.commit()
    print("✅ Tablas recreadas exitosamente")
    print(f"✅ {len(servicios)} servicios insertados")
    
except Exception as e:
    conn.rollback()
    print(f"❌ Error: {e}")
finally:
    cur.close()
    conn.close()
