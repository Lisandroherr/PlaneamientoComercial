import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Agregar columna familia si no existe
try:
    cursor.execute("ALTER TABLE precios ADD COLUMN familia TEXT")
    print("✅ Columna 'familia' agregada a la tabla precios")
except sqlite3.OperationalError:
    print("ℹ️ La columna 'familia' ya existe")

# Función para determinar la familia
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

# Obtener todos los modelos
cursor.execute("SELECT id, modelo FROM precios")
modelos = cursor.fetchall()

# Actualizar cada modelo con su familia
contador = 0
for id_modelo, modelo in modelos:
    familia = obtener_familia(modelo)
    cursor.execute("UPDATE precios SET familia = ? WHERE id = ?", (familia, id_modelo))
    contador += 1
    print(f"{contador}. {modelo[:50]:<50} → {familia}")

conn.commit()
conn.close()

print(f"\n✅ {contador} modelos actualizados con sus familias")
