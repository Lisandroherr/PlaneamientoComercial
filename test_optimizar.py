import psycopg2
import os
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
conn = psycopg2.connect(os.environ['DATABASE_URL'])
cursor = conn.cursor(cursor_factory=RealDictCursor)

fecha = '2025-12-06'

# Obtener operaciones
cursor.execute("""
    SELECT po.id, po.hora_inicio::TEXT, po.hora_fin::TEXT,
           col.duracion_minutos, i.estado, i.dominio
    FROM planificacion_operaciones po
    JOIN config_operaciones_lavado col ON po.operacion_lavado_id = col.id
    JOIN ingresos_usados i ON po.ingreso_id = i.id
    WHERE po.fecha_planificada::DATE = %s
    ORDER BY po.hora_inicio ASC
""", (fecha,))
operaciones = cursor.fetchall()

print(f"\n=== SIMULACIÓN DE OPTIMIZACIÓN {fecha} ===\n")

# Obtener configuración de jornada
cursor.execute("""
    SELECT tipo_jornada FROM config_jornadas_lavadero WHERE fecha = %s
""", (fecha,))
config_jornada = cursor.fetchone()

if config_jornada and config_jornada['tipo_jornada'] == 'corrida':
    print("Tipo de jornada: CORRIDA (08:30 - 17:30)")
    minuto_inicio = 8 * 60 + 30
    minuto_fin_jornada = 17 * 60 + 30
    tiene_descanso = False
else:
    print("Tipo de jornada: CORTADA (08:30-13:00 y 16:00-20:00)")
    minuto_inicio = 8 * 60 + 30
    minuto_fin_manana = 13 * 60
    minuto_inicio_tarde = 16 * 60
    minuto_fin_jornada = 20 * 60
    tiene_descanso = True

# Verificar si es hoy
fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
hoy = datetime.now().date()
fecha_operacion = fecha_obj.date()
es_hoy = (hoy == fecha_operacion)

print(f"Es hoy: {es_hoy}")
if es_hoy:
    ahora = datetime.now()
    minuto_actual = ahora.hour * 60 + ahora.minute
    print(f"Hora actual: {ahora.hour:02d}:{ahora.minute:02d} (minuto {minuto_actual})")
else:
    minuto_actual = -1

print(f"\n--- Operaciones originales ---")
for op in operaciones:
    print(f"{op['dominio']:8} | {op['hora_inicio']} - {op['hora_fin']} ({op['duracion_minutos']}min) | Estado: {op['estado']}")

print(f"\n--- Simulación de optimización ---")
tiempo_actual = minuto_inicio
operaciones_movidas = 0

for operacion in operaciones:
    duracion = operacion['duracion_minutos']
    estado = operacion.get('estado', 'Reservado')
    dominio = operacion['dominio']
    
    # Parsear hora_inicio de la operación
    hora_op_str = operacion['hora_inicio']
    h_op, m_op = map(int, hora_op_str.split(':')[:2])
    minuto_inicio_op = h_op * 60 + m_op
    
    print(f"\n{dominio}: Original {hora_op_str} (minuto {minuto_inicio_op})")
    
    # Si la operación está completada
    if estado in ['Salón', 'Completado']:
        print(f"  ⏩ OMITIR: Estado {estado} (operación completada)")
        hora_fin_str = operacion['hora_fin']
        h_fin, m_fin = map(int, hora_fin_str.split(':')[:2])
        tiempo_actual = h_fin * 60 + m_fin
        continue
    
    # Si la operación ya terminó o está en curso
    if es_hoy and minuto_inicio_op <= minuto_actual:
        print(f"  ⏩ OMITIR: Ya pasó o está en curso (minuto {minuto_inicio_op} <= {minuto_actual})")
        hora_fin_str = operacion['hora_fin']
        h_fin, m_fin = map(int, hora_fin_str.split(':')[:2])
        tiempo_actual = h_fin * 60 + m_fin
        continue
    
    # Verificar si cabe en horario laboral
    if tiene_descanso:
        hora_fin_prevista = tiempo_actual + duracion
        if tiempo_actual < minuto_fin_manana and hora_fin_prevista > minuto_fin_manana:
            tiempo_actual = minuto_inicio_tarde
            print(f"  ⚠️ Saltando al inicio de la tarde (minuto {tiempo_actual})")
    else:
        hora_fin_prevista = tiempo_actual + duracion
        if hora_fin_prevista > minuto_fin_jornada:
            print(f"  ❌ No cabe más operaciones (terminaría en minuto {hora_fin_prevista} > {minuto_fin_jornada})")
            break
    
    # Nueva hora
    hora_inicio_nueva = f"{tiempo_actual // 60:02d}:{tiempo_actual % 60:02d}:00"
    tiempo_actual += duracion
    hora_fin_nueva = f"{tiempo_actual // 60:02d}:{tiempo_actual % 60:02d}:00"
    
    print(f"  Nueva: {hora_inicio_nueva} - {hora_fin_nueva}")
    
    if hora_inicio_nueva != operacion['hora_inicio']:
        print(f"  ✅ SE MOVERÍA (diferente de {operacion['hora_inicio']})")
        operaciones_movidas += 1
    else:
        print(f"  ⏸️ NO SE MUEVE (ya está en {hora_inicio_nueva})")

print(f"\n=== RESULTADO ===")
print(f"Operaciones que se moverían: {operaciones_movidas} de {len(operaciones)}")

conn.close()
