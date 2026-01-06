import psycopg2
import os
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.environ['DATABASE_URL'])
cursor = conn.cursor(cursor_factory=RealDictCursor)

fecha = '2025-12-06'

# Consultar operaciones
cursor.execute("""
    SELECT po.id, i.dominio, po.hora_inicio::TEXT, po.hora_fin::TEXT, 
           col.duracion_minutos, i.estado
    FROM planificacion_operaciones po
    JOIN config_operaciones_lavado col ON po.operacion_lavado_id = col.id
    JOIN ingresos_usados i ON po.ingreso_id = i.id
    WHERE po.fecha_planificada::DATE = %s
    ORDER BY po.hora_inicio ASC
""", (fecha,))

ops = cursor.fetchall()

print(f"\n=== Operaciones del {fecha} ===")
for op in ops:
    print(f"{op['dominio']:8} | {op['hora_inicio']} - {op['hora_fin']} ({op['duracion_minutos']}min) | Estado: {op['estado']}")

# Verificar configuración de jornada
cursor.execute("""
    SELECT tipo_jornada FROM config_jornadas_lavadero WHERE fecha = %s
""", (fecha,))
config = cursor.fetchone()

if config:
    print(f"\nTipo de jornada: {config['tipo_jornada']}")
else:
    print("\nTipo de jornada: cortada (por defecto)")

conn.close()
