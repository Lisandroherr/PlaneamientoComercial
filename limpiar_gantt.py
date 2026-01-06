#!/usr/bin/env python3
"""
Script de limpieza COMPLETA del módulo USADOS
Elimina TODOS los registros de las tablas relacionadas con el módulo de usados
ADVERTENCIA: Esta operación es IRREVERSIBLE
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from db_config import get_db_connection
from datetime import datetime

def limpiar_gantt():
    """Limpia el Gantt de operaciones huérfanas y datos antiguos"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("=" * 70)
        print(" SCRIPT DE LIMPIEZA DEL GANTT")
        print("=" * 70)
        print()
        
        # 1. Eliminar operaciones sin vehículo asociado (huérfanas de ingresos_usados)
        print("📋 Buscando operaciones huérfanas de ingresos_usados...")
        cursor.execute("""
            DELETE FROM planificacion_operaciones
            WHERE ingreso_id IS NOT NULL
            AND ingreso_id NOT IN (SELECT id FROM ingresos_usados)
            RETURNING id, fecha_planificada, ingreso_id
        """)
        ops_huerfanas_usados = cursor.fetchall()
        
        if ops_huerfanas_usados:
            print(f"   ✅ Eliminadas {len(ops_huerfanas_usados)} operaciones huérfanas de usados:")
            for op in ops_huerfanas_usados[:5]:  # Mostrar máximo 5
                print(f"      - ID: {op['id']}, Fecha: {op['fecha_planificada']}, Ingreso ID: {op['ingreso_id']}")
            if len(ops_huerfanas_usados) > 5:
                print(f"      ... y {len(ops_huerfanas_usados) - 5} más")
        else:
            print("   ℹ️  No se encontraron operaciones huérfanas de usados")
        
        print()
        
        # 2. Eliminar operaciones sin ninguna referencia
        print("📋 Buscando operaciones sin referencias...")
        cursor.execute("""
            DELETE FROM planificacion_operaciones
            WHERE ingreso_id IS NULL
            RETURNING id, fecha_planificada
        """)
        ops_sin_referencia = cursor.fetchall()
        
        if ops_sin_referencia:
            print(f"   ✅ Eliminadas {len(ops_sin_referencia)} operaciones sin referencias:")
            for op in ops_sin_referencia[:5]:
                print(f"      - ID: {op['id']}, Fecha: {op['fecha_planificada']}")
            if len(ops_sin_referencia) > 5:
                print(f"      ... y {len(ops_sin_referencia) - 5} más")
        else:
            print("   ℹ️  No se encontraron operaciones sin referencias")
        
        print()
        
        # 4. Contar reservas KINTO existentes
        print("📋 Verificando reservas KINTO...")
        cursor.execute("""
            SELECT COUNT(*) as count FROM reservas_kinto
        """)
        count_kinto_inactivas = cursor.fetchone()['count']
        
        if count_kinto_inactivas > 0:
            print(f"   ℹ️  Se encontraron {count_kinto_inactivas} reservas KINTO (se limpiarán con opción 2)")
        else:
            print(f"   ℹ️  No se encontraron reservas KINTO")
        
        print()
        
        # 5. Resumen de limpieza
        print("=" * 70)
        print(" RESUMEN DE LIMPIEZA")
        print("=" * 70)
        
        total_eliminadas = len(ops_huerfanas_usados) + len(ops_sin_referencia)
        
        print(f"✅ Total de operaciones eliminadas: {total_eliminadas}")
        print(f"   - Huérfanas de usados: {len(ops_huerfanas_usados)}")
        print(f"   - Sin referencias: {len(ops_sin_referencia)}")
        print(f"ℹ️  Reservas KINTO encontradas: {count_kinto_inactivas} (use opción 2 para eliminarlas)")
        print()
        
        # 6. Estado actual del Gantt
        cursor.execute("SELECT COUNT(*) as count FROM planificacion_operaciones")
        ops_restantes = cursor.fetchone()['count']
        
        cursor.execute("""
            SELECT COUNT(*) as count FROM planificacion_operaciones 
            WHERE ingreso_id IS NOT NULL
        """)
        ops_usados = cursor.fetchone()['count']
        
        print("📊 Estado actual del Gantt:")
        print(f"   - Total operaciones: {ops_restantes}")
        print(f"   - Operaciones Usados: {ops_usados}")
        print()
        
        # Confirmar cambios
        conn.commit()
        print("✅ Cambios guardados exitosamente")
        print()
        print("=" * 70)
        print(" LIMPIEZA COMPLETADA")
        print("=" * 70)
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ ERROR durante la limpieza: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def limpiar_vehiculos_inactivos():
    """Elimina definitivamente vehículos marcados como inactivos"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print()
        print("=" * 70)
        print(" LIMPIEZA DE VEHÍCULOS INACTIVOS")
        print("=" * 70)
        print()
        
        # Contar vehículos inactivos
        cursor.execute("SELECT COUNT(*) as count FROM ingresos_usados WHERE activo = FALSE")
        count_inactivos = cursor.fetchone()['count']
        
        if count_inactivos > 0:
            # Obtener detalles de vehículos inactivos
            cursor.execute("""
                SELECT i.id, i.dominio, m1.nombre as marca_nombre, m2.nombre as modelo_nombre, i.estado 
                FROM ingresos_usados i
                LEFT JOIN marcas_usados m1 ON i.marca_id = m1.id
                LEFT JOIN modelos_usados m2 ON i.modelo_id = m2.id
                WHERE i.activo = FALSE
                ORDER BY i.id
            """)
            vehiculos_inactivos = cursor.fetchall()
            
            print(f"📋 Se encontraron {count_inactivos} vehículos inactivos:")
            for v in vehiculos_inactivos[:10]:  # Mostrar máximo 10
                print(f"   - ID: {v['id']}, Dominio: {v['dominio']}, Estado: {v['estado']}")
            if count_inactivos > 10:
                print(f"   ... y {count_inactivos - 10} más")
            print()
            
            respuesta = input("¿Desea eliminar estos vehículos permanentemente? (s/N): ").strip().lower()
            
            if respuesta == 's':
                cursor.execute("DELETE FROM ingresos_usados WHERE activo = FALSE")
                conn.commit()
                print(f"✅ Eliminados {count_inactivos} vehículos inactivos")
            else:
                print("ℹ️  Operación cancelada. Los vehículos inactivos se mantienen.")
        else:
            print("ℹ️  No se encontraron vehículos inactivos")
        
        print()
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ ERROR: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def verificar_integridad():
    """Verifica la integridad de los datos después de la limpieza"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("=" * 70)
        print(" VERIFICACIÓN DE INTEGRIDAD")
        print("=" * 70)
        print()
        
        # Verificar operaciones con referencias válidas
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM planificacion_operaciones po
            WHERE po.ingreso_id IS NOT NULL 
              AND po.ingreso_id NOT IN (SELECT id FROM ingresos_usados)
        """)
        referencias_invalidas = cursor.fetchone()['count']
        
        if referencias_invalidas > 0:
            print(f"⚠️  ADVERTENCIA: Se encontraron {referencias_invalidas} operaciones con referencias inválidas")
        else:
            print("✅ Todas las operaciones tienen referencias válidas")
        
        # Verificar stock clasificado correctamente
        cursor.execute("""
            SELECT 
                COALESCE(clasificacion, 'USADOS') as clasificacion, 
                COUNT(*) as count 
            FROM ingresos_usados 
            GROUP BY clasificacion
        """)
        stock_por_clasificacion = cursor.fetchall()
        
        print()
        print("📊 Stock actual por clasificación:")
        for item in stock_por_clasificacion:
            print(f"   - {item['clasificacion']}: {item['count']} vehículos")
        
        print()
        print("✅ Verificación completada")
        print()
        
    except Exception as e:
        print(f"\n❌ ERROR durante verificación: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def vaciar_modulo_usados_completo():
    """Vacía COMPLETAMENTE todas las tablas del módulo usados"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print()
        print("=" * 70)
        print(" VACIADO COMPLETO DEL MÓDULO USADOS")
        print("=" * 70)
        print()
        print("⚠️  ADVERTENCIA: Esta operación eliminará TODOS los datos de:")
        print("   - Planificación de operaciones (Gantt)")
        print("   - Reservas KINTO")
        print("   - Historial de estados")
        print("   - Ingresos de vehículos usados")
        print("   - Marcas y modelos personalizados")
        print()
        print("⚠️  ESTO NO SE PUEDE DESHACER")
        print()
        
        # Mostrar contadores antes de borrar
        print("📊 Estado actual ANTES de la limpieza:")
        
        cursor.execute("SELECT COUNT(*) as count FROM planificacion_operaciones")
        count_ops = cursor.fetchone()['count']
        print(f"   - Operaciones en Gantt: {count_ops}")
        
        cursor.execute("SELECT COUNT(*) as count FROM reservas_kinto")
        count_kinto = cursor.fetchone()['count']
        print(f"   - Reservas KINTO: {count_kinto}")
        
        cursor.execute("SELECT COUNT(*) as count FROM historial_estados_usados")
        count_historial = cursor.fetchone()['count']
        print(f"   - Registros en historial: {count_historial}")
        
        cursor.execute("SELECT COUNT(*) as count FROM ingresos_usados")
        count_ingresos = cursor.fetchone()['count']
        print(f"   - Vehículos ingresados: {count_ingresos}")
        
        cursor.execute("SELECT COUNT(*) as count FROM modelos_usados")
        count_modelos = cursor.fetchone()['count']
        print(f"   - Modelos de vehículos: {count_modelos}")
        
        cursor.execute("SELECT COUNT(*) as count FROM marcas_usados")
        count_marcas = cursor.fetchone()['count']
        print(f"   - Marcas de vehículos: {count_marcas}")
        
        print()
        print("=" * 70)
        respuesta = input("¿Está SEGURO que desea ELIMINAR TODOS estos datos? (escriba 'ELIMINAR' para confirmar): ").strip()
        
        if respuesta != 'ELIMINAR':
            print()
            print("ℹ️  Operación cancelada. No se eliminó ningún dato.")
            print()
            return
        
        print()
        print("🗑️  Iniciando limpieza completa...")
        print()
        
        # 1. Eliminar planificación de operaciones (esto incluye las de KINTO)
        print("1️⃣  Eliminando planificación de operaciones...")
        cursor.execute("DELETE FROM planificacion_operaciones")
        ops_eliminadas = cursor.rowcount
        print(f"   ✅ Eliminadas {ops_eliminadas} operaciones del Gantt")
        
        # 2. Eliminar reservas KINTO
        print("2️⃣  Eliminando reservas KINTO...")
        cursor.execute("DELETE FROM reservas_kinto")
        kinto_eliminadas = cursor.rowcount
        print(f"   ✅ Eliminadas {kinto_eliminadas} reservas KINTO")
        
        # 3. Eliminar historial de estados
        print("3️⃣  Eliminando historial de estados...")
        cursor.execute("DELETE FROM historial_estados_usados")
        historial_eliminado = cursor.rowcount
        print(f"   ✅ Eliminados {historial_eliminado} registros de historial")
        
        # 4. Eliminar ingresos de vehículos
        print("4️⃣  Eliminando vehículos ingresados...")
        cursor.execute("DELETE FROM ingresos_usados")
        ingresos_eliminados = cursor.rowcount
        print(f"   ✅ Eliminados {ingresos_eliminados} vehículos")
        
        # 5. Eliminar modelos (excepto los del sistema)
        print("5️⃣  Eliminando modelos personalizados...")
        cursor.execute("DELETE FROM modelos_usados")
        modelos_eliminados = cursor.rowcount
        print(f"   ✅ Eliminados {modelos_eliminados} modelos")
        
        # 6. Eliminar marcas (excepto las del sistema)
        print("6️⃣  Eliminando marcas personalizadas...")
        cursor.execute("DELETE FROM marcas_usados")
        marcas_eliminadas = cursor.rowcount
        print(f"   ✅ Eliminadas {marcas_eliminadas} marcas")
        
        # 7. Resetear secuencias (para que los IDs empiecen desde 1)
        print("7️⃣  Reseteando secuencias de IDs...")
        cursor.execute("ALTER SEQUENCE planificacion_operaciones_id_seq RESTART WITH 1")
        cursor.execute("ALTER SEQUENCE reservas_kinto_id_seq RESTART WITH 1")
        cursor.execute("ALTER SEQUENCE historial_estados_usados_id_seq RESTART WITH 1")
        cursor.execute("ALTER SEQUENCE ingresos_usados_id_seq RESTART WITH 1")
        cursor.execute("ALTER SEQUENCE modelos_usados_id_seq RESTART WITH 1")
        cursor.execute("ALTER SEQUENCE marcas_usados_id_seq RESTART WITH 1")
        print("   ✅ Secuencias reseteadas")
        
        # Confirmar cambios
        conn.commit()
        
        print()
        print("=" * 70)
        print(" RESUMEN DE LIMPIEZA")
        print("=" * 70)
        print(f"✅ Operaciones Gantt eliminadas: {ops_eliminadas}")
        print(f"✅ Reservas KINTO eliminadas: {kinto_eliminadas}")
        print(f"✅ Registros historial eliminados: {historial_eliminado}")
        print(f"✅ Vehículos eliminados: {ingresos_eliminados}")
        print(f"✅ Modelos eliminados: {modelos_eliminados}")
        print(f"✅ Marcas eliminadas: {marcas_eliminadas}")
        print()
        
        # Verificar que todo esté vacío
        cursor.execute("SELECT COUNT(*) as count FROM planificacion_operaciones")
        if cursor.fetchone()['count'] == 0:
            print("✅ Gantt completamente limpio")
        
        cursor.execute("SELECT COUNT(*) as count FROM ingresos_usados")
        if cursor.fetchone()['count'] == 0:
            print("✅ Tabla de vehículos completamente limpia")
        
        cursor.execute("SELECT COUNT(*) as count FROM reservas_kinto")
        if cursor.fetchone()['count'] == 0:
            print("✅ Reservas KINTO completamente limpias")
        
        print()
        print("=" * 70)
        print(" LIMPIEZA COMPLETA EXITOSA")
        print("=" * 70)
        print()
        print("ℹ️  El módulo de usados está completamente vacío y listo para usar.")
        print()
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ ERROR durante la limpieza: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    try:
        print()
        print("╔═══════════════════════════════════════════════════════════════════╗")
        print("║       LIMPIEZA COMPLETA DEL MÓDULO USADOS                       ║")
        print("╚═══════════════════════════════════════════════════════════════════╝")
        print()
        print("Este script ofrece DOS opciones:")
        print()
        print("  [1] Limpieza Selectiva (huérfanas e inconsistencias)")
        print("      - Elimina solo operaciones huérfanas")
        print("      - Elimina reservas inactivas")
        print("      - Limpia inconsistencias")
        print()
        print("  [2] VACIADO COMPLETO (⚠️  PELIGROSO)")
        print("      - Elimina TODOS los vehículos")
        print("      - Elimina TODAS las operaciones")
        print("      - Elimina TODAS las reservas KINTO")
        print("      - Elimina marcas y modelos")
        print("      - Resetea el Gantt completamente")
        print()
        
        opcion = input("Seleccione una opción (1 o 2, o Enter para cancelar): ").strip()
        
        if opcion == '1':
            print()
            print("═══ Opción 1: Limpieza Selectiva ═══")
            print()
            respuesta = input("¿Confirma esta opción? (s/N): ").strip().lower()
            if respuesta == 's':
                limpiar_gantt()
                limpiar_vehiculos_inactivos()
                verificar_integridad()
                print()
                print("╔═══════════════════════════════════════════════════════════════════╗")
                print("║                    PROCESO COMPLETADO                            ║")
                print("╚═══════════════════════════════════════════════════════════════════╝")
                print()
            else:
                print()
                print("ℹ️  Operación cancelada")
                print()
                
        elif opcion == '2':
            print()
            print("═══ Opción 2: VACIADO COMPLETO ═══")
            vaciar_modulo_usados_completo()
            
        else:
            print()
            print("ℹ️  Operación cancelada por el usuario")
            print()
            
    except Exception as e:
        print()
        print("=" * 70)
        print(" ERROR FATAL")
        print("=" * 70)
        print(f"❌ {e}")
        print()
        exit(1)
