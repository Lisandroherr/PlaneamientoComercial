"""
Script para crear las tablas del módulo Business Intelligence Analysis
"""
from db_config import get_db_connection, release_db_connection

def init_bi_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("🔧 Creando tablas para Business Intelligence Analysis...")
        
        # Tabla para patentamientos por MARCA
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bi_patentamientos_marca (
                id SERIAL PRIMARY KEY,
                marca VARCHAR(100) NOT NULL,
                ubicacion VARCHAR(50) NOT NULL,
                mes VARCHAR(10) NOT NULL,
                cantidad INTEGER NOT NULL DEFAULT 0,
                fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(marca, ubicacion, mes)
            )
        ''')
        print("✅ Tabla bi_patentamientos_marca creada")
        
        # Tabla para patentamientos por MODELO
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bi_patentamientos_modelo (
                id SERIAL PRIMARY KEY,
                modelo VARCHAR(200) NOT NULL,
                ubicacion VARCHAR(50) NOT NULL,
                mes VARCHAR(10) NOT NULL,
                cantidad INTEGER NOT NULL DEFAULT 0,
                fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(modelo, ubicacion, mes)
            )
        ''')
        print("✅ Tabla bi_patentamientos_modelo creada")
        
        # Tabla para entregas convencionales y especiales
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bi_entregas (
                id SERIAL PRIMARY KEY,
                modelo VARCHAR(200) NOT NULL,
                tipo_venta VARCHAR(50) NOT NULL,
                fecha_entrega DATE NOT NULL,
                cantidad INTEGER NOT NULL DEFAULT 1,
                fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ Tabla bi_entregas creada")
        
        # Tabla para plan de ahorro
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bi_plan_ahorro (
                id SERIAL PRIMARY KEY,
                modelo VARCHAR(200) NOT NULL,
                fecha_entrega DATE NOT NULL,
                cantidad INTEGER NOT NULL DEFAULT 1,
                fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ Tabla bi_plan_ahorro creada")
        
        # Tabla para plan de negocio (objetivos anuales)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bi_plan_negocio (
                id SERIAL PRIMARY KEY,
                modelo VARCHAR(200) NOT NULL,
                anio INTEGER NOT NULL,
                objetivo_anual INTEGER NOT NULL,
                fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(modelo, anio)
            )
        ''')
        print("✅ Tabla bi_plan_negocio creada")
        
        # Tabla para log de cargas de archivos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bi_archivos_cargados (
                id SERIAL PRIMARY KEY,
                nombre_archivo VARCHAR(255) NOT NULL,
                tipo_archivo VARCHAR(100) NOT NULL,
                fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                registros_procesados INTEGER DEFAULT 0,
                usuario VARCHAR(100)
            )
        ''')
        print("✅ Tabla bi_archivos_cargados creada")
        
        conn.commit()
        release_db_connection(conn)
        
        print("\n✅ ¡Todas las tablas de Business Intelligence creadas exitosamente!")
        
    except Exception as e:
        print(f"\n❌ Error al crear tablas: {e}")
        conn.rollback()
        release_db_connection(conn)

if __name__ == "__main__":
    init_bi_tables()
