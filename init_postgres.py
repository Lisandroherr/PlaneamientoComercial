import os
import json
from db_config import get_db_connection, release_db_connection, init_connection_pool

def init_postgres_database():
    """Inicializar todas las tablas en PostgreSQL"""
    
    print("🚀 Iniciando configuración de base de datos PostgreSQL...")
    
    # Inicializar pool de conexiones
    try:
        init_connection_pool()
    except Exception as e:
        print(f"❌ Error al inicializar pool: {e}")
        return False
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Crear tablas
        print("📋 Creando tablas...")
        
        # Tabla de precios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS precios (
                id SERIAL PRIMARY KEY,
                modelo TEXT UNIQUE NOT NULL,
                precio_ars REAL DEFAULT 0,
                precio_usd REAL DEFAULT 0,
                cotizacion REAL DEFAULT 1000,
                descuento REAL DEFAULT 0,
                visible INTEGER DEFAULT 1,
                dado_baja INTEGER DEFAULT 0,
                familia TEXT,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de unidades postergadas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS unidades_postergadas (
                id SERIAL PRIMARY KEY,
                numero_fabrica TEXT UNIQUE NOT NULL,
                fecha_agregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de disponibles
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS disponibles (
                id SERIAL PRIMARY KEY,
                numero_fabrica TEXT,
                numero_chasis TEXT,
                modelo_version TEXT,
                color TEXT,
                fecha_finanzas TEXT,
                despacho_estimado TEXT,
                entrega_estimada TEXT,
                fecha_recepcion TEXT,
                ubicacion TEXT,
                dias_stock TEXT,
                precio_disponible REAL,
                cod_cliente TEXT,
                cliente TEXT,
                vendedor TEXT,
                operacion TEXT,
                fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de unidades reservadas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS unidades_reservadas (
                id SERIAL PRIMARY KEY,
                numero_fabrica TEXT UNIQUE NOT NULL,
                vendedor TEXT,
                fecha_agregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de preventa
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS preventa (
                id SERIAL PRIMARY KEY,
                numero_fabrica TEXT DEFAULT 'YAC999999999',
                modelo_version TEXT,
                operacion TEXT,
                vendedor TEXT,
                color TEXT,
                informado INTEGER DEFAULT 0,
                cancelado INTEGER DEFAULT 0,
                asignado INTEGER DEFAULT 0,
                fecha_carga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de descuentos adicionales
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS descuentos_adicionales (
                id SERIAL PRIMARY KEY,
                tipo TEXT NOT NULL,
                clave TEXT NOT NULL,
                valor REAL DEFAULT 0,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(tipo, clave)
            )
        ''')
        
        conn.commit()
        print("✅ Tablas creadas exitosamente")
        
        # Verificar si ya hay datos
        cursor.execute('SELECT COUNT(*) as count FROM precios')
        count = cursor.fetchone()['count']
        
        if count > 0:
            print(f"ℹ️ La base de datos ya tiene {count} modelos. Saltando inicialización de datos.")
            release_db_connection(conn)
            return True
        
        print("📦 Insertando datos iniciales...")
        
        # Cargar modelos desde backup
        with open('backup_precios.json', 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        # Función para obtener familia
        def obtener_familia(modelo):
            modelo_upper = modelo.upper()
            if 'COROLLA CROSS' in modelo_upper:
                return 'COROLLA CROSS'
            elif 'COROLLA' in modelo_upper:
                return 'COROLLA'
            elif 'HILUX' in modelo_upper:
                return 'HILUX'
            elif 'SW4' in modelo_upper:
                return 'SW4'
            elif 'YARIS' in modelo_upper and ('GR' in modelo_upper or 'GR-SPORT' in modelo_upper):
                return 'YARIS GR'
            elif 'YARIS' in modelo_upper:
                return 'YARIS'
            elif 'HIACE' in modelo_upper:
                return 'HIACE'
            elif 'LAND CRUISER' in modelo_upper:
                return 'LAND CRUISER'
            elif 'RAV' in modelo_upper:
                return 'RAV 4'
            else:
                return 'OTROS'
        
        # Insertar modelos con precios
        for item in backup_data:
            familia = obtener_familia(item['modelo'])
            cursor.execute('''
                INSERT INTO precios (modelo, precio_ars, precio_usd, cotizacion, descuento, visible, dado_baja, familia)
                VALUES (%s, %s, %s, %s, %s, 1, %s, %s)
                ON CONFLICT (modelo) DO NOTHING
            ''', (
                item['modelo'],
                item['precio_ars'],
                item['precio_usd'],
                item['cotizacion'],
                item['descuento'],
                item.get('dado_baja', 0),
                familia
            ))
        
        print(f"✅ {len(backup_data)} modelos insertados")
        
        # Insertar unidades postergadas
        unidades_postergadas = [
            "YAC125090007", "YAC125090028", "YAC125090029", "YAC125090036", "YAC125090046",
            "YAC125090061", "YAC125090079", "YAC125090083", "YAC125090097", "YAC125080004"
        ]
        
        for numero in unidades_postergadas:
            cursor.execute('''
                INSERT INTO unidades_postergadas (numero_fabrica)
                VALUES (%s)
                ON CONFLICT (numero_fabrica) DO NOTHING
            ''', (numero,))
        
        print(f"✅ {len(unidades_postergadas)} unidades postergadas insertadas")
        
        # Insertar descuentos adicionales
        descuentos_default = [
            ('stock', 'descuento_stock', 0),
            ('color', 'super_blanco', 0),
            ('color', 'blanco_perlado', 0),
            ('color', 'gris_plata', 0),
            ('color', 'gris_azulado', 0),
            ('color', 'gris_oscuro', 0),
            ('color', 'rojo_metalizado', 0),
            ('color', 'negro_mica', 0),
            ('antiguedad', 'meses', 3),
            ('antiguedad', 'descuento', 0)
        ]
        
        for tipo, clave, valor in descuentos_default:
            cursor.execute('''
                INSERT INTO descuentos_adicionales (tipo, clave, valor)
                VALUES (%s, %s, %s)
                ON CONFLICT (tipo, clave) DO NOTHING
            ''', (tipo, clave, valor))
        
        print(f"✅ {len(descuentos_default)} descuentos adicionales configurados")
        
        conn.commit()
        print("✅ Base de datos PostgreSQL inicializada correctamente")
        
        release_db_connection(conn)
        return True
        
    except Exception as e:
        print(f"❌ Error al inicializar base de datos: {e}")
        conn.rollback()
        release_db_connection(conn)
        return False

if __name__ == '__main__':
    init_postgres_database()
