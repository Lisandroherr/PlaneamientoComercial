import psycopg2
from psycopg2 import sql
from db_config import get_db_connection

def init_postventa():
    """Inicializa las tablas del módulo Post Venta"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Tabla de servicios disponibles
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pv_servicios (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(255) NOT NULL UNIQUE,
                sector VARCHAR(50) NOT NULL CHECK (sector IN ('Servicios', 'Chapería y Pintura')),
                asignacion VARCHAR(255) DEFAULT 'Aleatorio',
                ranking_comisiones INTEGER CHECK (ranking_comisiones >= 1 AND ranking_comisiones <= 5),
                activo BOOLEAN DEFAULT TRUE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de asesores de post venta
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pv_asesores (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(255) NOT NULL,
                usuario_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                sector VARCHAR(50) NOT NULL CHECK (sector IN ('Servicios', 'Chapería y Pintura')),
                activo BOOLEAN DEFAULT TRUE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(usuario_id)
            )
        """)
        
        # Tabla de turnos importados
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pv_turnos (
                id SERIAL PRIMARY KEY,
                fec_turno DATE NOT NULL,
                hora_inicio TIME NOT NULL,
                dominio VARCHAR(50) NOT NULL,
                nombre_cliente VARCHAR(255) NOT NULL,
                servicio VARCHAR(255) NOT NULL,
                marca_modelo VARCHAR(255),
                sector VARCHAR(50) NOT NULL CHECK (sector IN ('Servicios', 'Chapería y Pintura')),
                asesor_id INTEGER REFERENCES pv_asesores(id) ON DELETE SET NULL,
                estado VARCHAR(50) DEFAULT 'Pendiente Asignación' 
                    CHECK (estado IN ('Pendiente Asignación', 'Asignado', 'En Atención', 'Hora Pactada', 'Entregado')),
                fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_asignacion TIMESTAMP
            )
        """)
        
        # Tabla de historial de acciones
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pv_historial (
                id SERIAL PRIMARY KEY,
                turno_id INTEGER REFERENCES pv_turnos(id) ON DELETE CASCADE UNIQUE,
                asesor_id INTEGER REFERENCES pv_asesores(id) ON DELETE SET NULL,
                servicio VARCHAR(255) NOT NULL,
                sector VARCHAR(50) NOT NULL,
                fecha_turno DATE NOT NULL,
                hora_atender TIMESTAMP,
                hora_pactada_registro TIMESTAMP,
                fecha_hora_pactada TIMESTAMP,
                hora_entregado TIMESTAMP,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insertar servicios predefinidos
        servicios_servicios = [
            ('ALINEAR Y BALANCEAR', 'Servicios', 3),
            ('CALADO Y CODIFICADO', 'Servicios', 4),
            ('CAMPAÑA BARRA CON CONTRAMEDIDA', 'Servicios', 2),
            ('COLOCACION PARABRISAS', 'Servicios', 3),
            ('CONTACTLESS DE 10.000KM', 'Servicios', 2),
            ('DIAGNOSTICO', 'Servicios', 3),
            ('Diagnóstico', 'Servicios', 3),
            ('DIAGNOSTICO DPF', 'Servicios', 4),
            ('EXPRESS 10.000 KM', 'Servicios', 2),
            ('EXPRESS 30.000 KM', 'Servicios', 2),
            ('EXPRESS 90.000 KM', 'Servicios', 2),
            ('FIR', 'Servicios', 5),
            ('Mantenimiento +150.000', 'Servicios', 4),
            ('Mantenimiento 1.000', 'Servicios', 2),
            ('Mantenimiento 10.000', 'Servicios', 3),
            ('Mantenimiento 100.000', 'Servicios', 4),
            ('Mantenimiento 110.000', 'Servicios', 4),
            ('Mantenimiento 120.000', 'Servicios', 4),
            ('Mantenimiento 130.000', 'Servicios', 4),
            ('Mantenimiento 170.000', 'Servicios', 5),
            ('Mantenimiento 180.000', 'Servicios', 5),
            ('Mantenimiento 20.000', 'Servicios', 3),
            ('Mantenimiento 30.000', 'Servicios', 3),
            ('Mantenimiento 40.000', 'Servicios', 3),
            ('Mantenimiento 50.000', 'Servicios', 4),
            ('Mantenimiento 60.000', 'Servicios', 4),
            ('Mantenimiento 70.000', 'Servicios', 4),
            ('Mantenimiento 80.000', 'Servicios', 4),
            ('Mantenimiento 90.000', 'Servicios', 4),
            ('Mantenimiento Express 10.000', 'Servicios', 2),
            ('Mantenimiento Express 20.000', 'Servicios', 2),
            ('Mantenimiento Express 30.000', 'Servicios', 2),
            ('Mantenimiento Express 40.000', 'Servicios', 2),
            ('Otros', 'Servicios', 1),
            ('PDS - PREPARACIÓN DE PREENTREGA', 'Servicios', 3),
            ('POLARIZADO', 'Servicios', 2),
            ('REP. EN GARANTIA', 'Servicios', 5),
            ('REP. GENERALES', 'Servicios', 3),
            ('Reparación', 'Servicios', 3),
            ('SERVICIO DE 1.000 KM', 'Servicios', 2),
            ('SERVICIO DE 10.000 KM', 'Servicios', 3),
            ('SERVICIO DE 100.000 KM', 'Servicios', 4),
            ('SERVICIO DE 20.000 KM', 'Servicios', 3),
            ('SERVICIO DE 30.000 KM', 'Servicios', 3),
            ('SERVICIO DE 40.000 KM', 'Servicios', 3),
            ('SERVICIO DE 50.000 KM', 'Servicios', 4),
            ('SERVICIO DE 60.000 KM', 'Servicios', 4),
            ('SERVICIO DE 70.000 KM', 'Servicios', 4),
            ('SERVICIO DE 80.000 KM', 'Servicios', 4),
            ('SERVICIO DE 90.000 KM', 'Servicios', 4),
        ]
        
        servicios_chaperia = [
            ('CH Y PINT PROPIA', 'Chapería y Pintura', 4),
            ('REP. DE CHAPERIA Y PINTURA', 'Chapería y Pintura', 5),
        ]
        
        all_servicios = servicios_servicios + servicios_chaperia
        
        for nombre, sector, ranking in all_servicios:
            cur.execute("""
                INSERT INTO pv_servicios (nombre, sector, ranking_comisiones, asignacion)
                VALUES (%s, %s, %s, 'Aleatorio')
                ON CONFLICT (nombre) DO NOTHING
            """, (nombre, sector, ranking))
        
        conn.commit()
        print("✅ Tablas de Post Venta creadas exitosamente")
        print(f"✅ {len(all_servicios)} servicios predefinidos insertados")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error al crear tablas de Post Venta: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    init_postventa()
