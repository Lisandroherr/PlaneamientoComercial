import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print("🔧 Corrigiendo datos inconsistentes en matriz_codigos_obs...")
    
    # CLASE A debe tener arribo SOLO en zona 4 (no en zona 3)
    print("\n1. CLASE A - Zona 3: Cambiar es_zona_arribo de TRUE a FALSE")
    cursor.execute("""
        UPDATE matriz_codigos_obs 
        SET es_zona_arribo = FALSE 
        WHERE clase = 'CLASE A' AND zona = 3
    """)
    
    # Verificar cambio
    cursor.execute("SELECT * FROM matriz_codigos_obs WHERE clase = 'CLASE A' ORDER BY zona")
    rows = cursor.fetchall()
    for row in rows:
        arribo = " ✨ ARRIBO" if row['es_zona_arribo'] else ""
        print(f"   {row['clase']} - Zona {row['zona']}: '{row['codigos']}'{arribo}")
    
    # Commit cambios
    conn.commit()
    print("\n✅ Cambios guardados correctamente")
    
    # Verificar que cada clase tenga exactamente 1 zona de arribo
    print("\n📊 Verificación final - Zonas de Arribo por Clase:")
    cursor.execute("""
        SELECT clase, zona, codigos, es_zona_arribo 
        FROM matriz_codigos_obs 
        WHERE es_zona_arribo = TRUE 
        ORDER BY clase
    """)
    arribes = cursor.fetchall()
    
    for row in arribes:
        print(f"   {row['clase']} → Zona {row['zona']} ✨")
    
    # Contar arribes por clase
    cursor.execute("""
        SELECT clase, COUNT(*) as total_arribes
        FROM matriz_codigos_obs 
        WHERE es_zona_arribo = TRUE 
        GROUP BY clase
        ORDER BY clase
    """)
    conteo = cursor.fetchall()
    
    print("\n📈 Conteo de Zonas de Arribo por Clase:")
    error = False
    for row in conteo:
        status = "✅" if row['total_arribes'] == 1 else "❌"
        print(f"   {status} {row['clase']}: {row['total_arribes']} arribo(s)")
        if row['total_arribes'] != 1:
            error = True
    
    if error:
        print("\n⚠️ ADVERTENCIA: Hay clases con múltiples o ninguna zona de arribo")
    else:
        print("\n✅ Todas las clases tienen exactamente 1 zona de arribo")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
