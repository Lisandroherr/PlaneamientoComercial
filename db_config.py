import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
try:
    load_dotenv()
except Exception as e:
    print(f"⚠️ Advertencia: No se pudo cargar .env: {e}")

# Pool de conexiones para mejor rendimiento
connection_pool = None

def init_connection_pool():
    """Inicializar pool de conexiones a PostgreSQL"""
    global connection_pool
    
    # Obtener URL de conexión desde variable de entorno
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        raise ValueError("❌ DATABASE_URL no está configurada")
    
    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            1, 20,  # mínimo 1, máximo 20 conexiones
            database_url,
            cursor_factory=RealDictCursor
        )
        print("✅ Pool de conexiones PostgreSQL inicializado")
        return connection_pool
    except Exception as e:
        print(f"❌ Error al conectar con PostgreSQL: {e}")
        raise

def get_db_connection():
    """Obtener conexión del pool"""
    global connection_pool
    
    if connection_pool is None:
        init_connection_pool()
    
    return connection_pool.getconn()

def release_db_connection(conn):
    """Devolver conexión al pool"""
    global connection_pool
    
    if connection_pool is not None and conn is not None:
        connection_pool.putconn(conn)

def close_all_connections():
    """Cerrar todas las conexiones del pool"""
    global connection_pool
    
    if connection_pool is not None:
        connection_pool.closeall()
        print("✅ Pool de conexiones cerrado")
