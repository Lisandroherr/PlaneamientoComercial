"""
Script para crear las tablas del módulo Business Intelligence Analysis
"""
from db_config import get_db_connection, release_db_connection

def init_bi_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Tabla para almacenar datos de patentamientos por MARCA
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bi_patentamientos_marca (
                id SERIAL PRIMARY KEY,
                ubicacion VARCHAR(50) NOT NULL,
                marca VARCHAR(100) NOT NULL,
                periodo VARCHAR(10) NOT NULL,
                cantidad INTEGER NOT NULL,
                fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ubicacion, marca, periodo)
            )
        ''')
        
        # Tabla para almacenar datos de patentamientos por MODELO
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bi_patentamientos_modelo (
                id SERIAL PRIMARY KEY,
                ubicacion VARCHAR(50) NOT NULL,
                modelo VARCHAR(200) NOT NULL,
                periodo VARCHAR(10) NOT NULL,
                cantidad INTEGER NOT NULL,
                fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ubicacion, modelo, periodo)
            )
        ''')
        
        # Tabla para almacenar datos de entregas - Ventas Convencionales
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bi_entregas_convencionales (
                id SERIAL PRIMARY KEY,
                fecha_entrega DATE NOT NULL,
                modelo VARCHAR(200) NOT NULL,
                cantidad INTEGER DEFAULT 1,
                fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla para almacenar datos de entregas - Ventas Especiales
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bi_entregas_especiales (
                id SERIAL PRIMARY KEY,
                fecha_entrega DATE NOT NULL,
                modelo VARCHAR(200) NOT NULL,
                cantidad INTEGER DEFAULT 1,
                fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla para almacenar datos de entregas - Plan de Ahorro
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bi_entregas_plan_ahorro (
                id SERIAL PRIMARY KEY,
                fecha_entrega DATE NOT NULL,
                modelo VARCHAR(200) NOT NULL,
                cantidad INTEGER DEFAULT 1,
                fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla para el plan de negocio (objetivos anuales por modelo)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bi_plan_negocio (
                id SERIAL PRIMARY KEY,
                anio INTEGER NOT NULL,
                modelo VARCHAR(200) NOT NULL,
                objetivo_anual INTEGER NOT NULL,
                fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(anio, modelo)
            )
        ''')
        
        # Índices para mejorar rendimiento
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pat_marca_periodo ON bi_patentamientos_marca(periodo)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pat_modelo_periodo ON bi_patentamientos_modelo(periodo)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entregas_conv_fecha ON bi_entregas_convencionales(fecha_entrega)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entregas_esp_fecha ON bi_entregas_especiales(fecha_entrega)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entregas_pa_fecha ON bi_entregas_plan_ahorro(fecha_entrega)')
        
        conn.commit()
        print("✅ Tablas de Business Intelligence creadas exitosamente")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creando tablas BI: {e}")
    finally:
        release_db_connection(conn)

if __name__ == '__main__':
    init_bi_tables()
