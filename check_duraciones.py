from db_config import get_db_connection
import psycopg2.extras

conn = get_db_connection()
cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
cursor.execute("SELECT nombre, duracion_minutos FROM config_operaciones_lavado ORDER BY duracion_minutos DESC")
ops = cursor.fetchall()

print("\n=== DURACIONES DE OPERACIONES ===")
for op in ops:
    print(f"{op['nombre']}: {op['duracion_minutos']} minutos")

cursor.close()
conn.close()
