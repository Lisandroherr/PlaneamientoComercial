"""
Crear tabla de evaluaciones mensuales de empleados
"""
from db_config import get_db_connection, release_db_connection

print("=" * 60)
print("🔧 CREANDO TABLA DE EVALUACIONES MENSUALES")
print("=" * 60)

conn = get_db_connection()
cursor = conn.cursor()

try:
    # Crear tabla de evaluaciones mensuales
    print("\n➕ Creando tabla evaluaciones_mensuales...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evaluaciones_mensuales (
            id SERIAL PRIMARY KEY,
            empleado_id INTEGER NOT NULL REFERENCES empleados(id) ON DELETE CASCADE,
            supervisor_id INTEGER NOT NULL REFERENCES supervisores(id) ON DELETE CASCADE,
            mes INTEGER NOT NULL CHECK (mes >= 1 AND mes <= 12),
            anio INTEGER NOT NULL,
            performance DECIMAL(5,2) DEFAULT 0 CHECK (performance >= 0 AND performance <= 100),
            comisiones DECIMAL(12,2) DEFAULT 0,
            anticipo_comisiones DECIMAL(12,2) DEFAULT 0,
            horas_extras_50 DECIMAL(6,2) DEFAULT 0,
            horas_extras_100 DECIMAL(6,2) DEFAULT 0,
            fecha_evaluacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(empleado_id, mes, anio)
        )
    """)
    print("   ✅ Tabla evaluaciones_mensuales creada")
    
    # Crear índices
    print("\n➕ Creando índices...")
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_evaluaciones_empleado 
        ON evaluaciones_mensuales(empleado_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_evaluaciones_supervisor 
        ON evaluaciones_mensuales(supervisor_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_evaluaciones_periodo 
        ON evaluaciones_mensuales(mes, anio)
    """)
    print("   ✅ Índices creados")
    
    conn.commit()
    
    print("\n" + "=" * 60)
    print("✅ TABLA DE EVALUACIONES CREADA EXITOSAMENTE")
    print("=" * 60)
    print("\nLa tabla permite:")
    print("  • Registrar performance (0-100%)")
    print("  • Registrar comisiones y anticipos")
    print("  • Registrar horas extras al 50% y 100%")
    print("  • Una evaluación por empleado por mes/año")
    print("  • Trazabilidad de fechas de evaluación")
    
except Exception as e:
    conn.rollback()
    print(f"\n❌ ERROR: {e}")
    
finally:
    release_db_connection(conn)
