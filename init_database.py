import sqlite3
import os

# Eliminar base de datos si existe
if os.path.exists('database.db'):
    os.remove('database.db')
    print("🗑️ Base de datos anterior eliminada")

# Crear conexión
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Crear tablas
cursor.execute('''
    CREATE TABLE IF NOT EXISTS precios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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

cursor.execute('''
    CREATE TABLE IF NOT EXISTS unidades_postergadas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_fabrica TEXT UNIQUE NOT NULL,
        fecha_agregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS disponibles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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

cursor.execute('''
    CREATE TABLE IF NOT EXISTS unidades_reservadas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_fabrica TEXT UNIQUE NOT NULL,
        vendedor TEXT,
        fecha_agregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS preventa (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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

cursor.execute('''
    CREATE TABLE IF NOT EXISTS descuentos_adicionales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL,
        clave TEXT NOT NULL,
        valor REAL DEFAULT 0,
        fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(tipo, clave)
    )
''')

print("✅ Tablas creadas")

# Lista de modelos (67 modelos - agregando los faltantes)
modelos = [
    "COROLLA 2.0 SEG CVT",
    "COROLLA 2.0 XEI SAFETY CVT",
    "COROLLA 2.0 XLI CVT",
    "COROLLA 2.0 XLI SAFETY CVT",
    "COROLLA CROSS GR-SPORT SAFETY 2.0 CVT",
    "COROLLA CROSS HEV 1.8 SEG ECVT",
    "COROLLA CROSS SEG HEV SAFETY 1.8 ECVT",
    "COROLLA CROSS SEG SAFETY 2.0 CVT",
    "COROLLA CROSS XEI HEV 1.8 ECVT",
    "COROLLA CROSS XEI HEV SAFETY 1.8 ECVT",
    "COROLLA CROSS XEI SAFETY 2.0 CVT",
    "COROLLA CROSS XLI SAFETY 2.0 CVT",
    "COROLLA HEV 1.8 XEI ECVT",
    "COROLLA HEV 1.8 XEI SAFETY eCVT",
    "ETIOS XLS PACK 1.5 4A/T 4P",
    "GR SUPRA",
    "GR YARIS",
    "HIACE FURGON L1H1 2.8 TDI 6AT 3A 4P",
    "HIACE FURGON L2H2 2.8 TDI 6 AT 3A 5P",
    "HIACE WAGON 2.8 TDI 6AT 10A",
    "HILUX 4X2 C/S DX 2.4 TDI 6 M/T",
    "HILUX 4X2 CC DX 2.4 TDI 6 M/T",
    "HILUX 4X2 D/C DX 2.4 TDI 6 A/T",
    "HILUX 4X2 D/C DX 2.4 TDI 6 M/T",
    "HILUX 4X2 D/C SR 2.4 TDI 6 A/T",
    "HILUX 4X2 D/C SR 2.4 TDI 6 M/T",
    "HILUX 4X2 D/C SRV 2.8 TDI 6 A/T",
    "HILUX 4X2 D/C SRX 2.8 TDI 6A/T",
    "HILUX 4X4 C/S DX 2.4 TDI 6M/T",
    "HILUX 4X4 CC DX 2.4 TDI 6 M/T",
    "HILUX 4X4 D/C DX 2.4 TDI 6 A/T",
    "HILUX 4X4 D/C DX 2.4 TDI 6M/T",
    "HILUX 4X4 D/C SR 2.8 TDI 6A/T",
    "HILUX 4X4 D/C SR 2.8 TDI 6MT",
    "HILUX 4X4 D/C SRV 2.8 TDI 6A/T",
    "HILUX 4X4 D/C SRV 2.8 TDI 6M/T",
    "HILUX 4X4 D/C SRX 2.8 TDI 6A/T",
    "HILUX 4X4 DC GR-SPORT IV 2.8 TDI 6 AT",
    "HILUX 4X4 DC SRV+ 2.8 TDI 6 AT",
    "LAND CRUISER 200 VX",
    "LAND CRUISER 300 VX",
    "LAND CRUISER PRADO VX A/T",
    "RAV 4 HEV 2.5 AWD Limited CVT",
    "SW4 4X4 DIAMOND 2.8 TDI 6 A/T 7A",
    "SW4 4X4 GR-S TDI 6AT 7A",
    "SW4 4X4 SRX 2.8 TDI 6 A/T 7A",
    "YARIS S 1.5 CVT 5P",
    "YARIS XLS 1.5 CVT 5P",
    "YARIS XLS PACK 1.5 CVT 4P",
    "YARIS XLS+ 1.5 CVT 5P",
    "YARIS XS 1.5 6M/T 5P",
    "YARIS XS 1.5 CVT 5P",
    "SC - COROLLA 2.0 SEG SAFETY CVT",
    "SC - COROLLA GR-SPORT SAFETY 2.0 CVT",
    "SC - COROLLA HEV 1.8 SEG SAFETY eCVT",
    "SC - HILUX 4X2 D/C SR 2.4 TDI 6 M/T",
    "SC - HILUX 4X2 D/C SR 2.4 TDI 6A/T",
    "SC - HILUX 4X2 D/C SRV 2.8 TDI 6A/T",
    "SC - HILUX 4X2 D/C SRX 2.8 TDI 6A/T",
    "SC - HILUX 4X4 D/C SR 2.8 TDI 6A/T",
    "SC - HILUX 4X4 D/C SR 2.8 TDI 6MT",
    "SC - HILUX 4X4 D/C SRV 2.8 TDI 6A/T",
    "SC - HILUX 4X4 D/C SRX 2.8 TDI 6A/T",
    "SC - HILUX D/C GR-S SPORT IV 2.8 TDI 6AT",
    "SC - SW4 4X4 DIAMOND 2.8 TDI 6 A/T 7A",
    "SC - SW4 4X4 GR-S TDI 6AT 7A",
    "SC - SW4 4X4 SRX 2.8 TDI 6A/T 7A"
]

# Cargar precios desde backup si existe
import json
precios_backup = {}
try:
    with open('backup_precios.json', 'r', encoding='utf-8') as f:
        backup_data = json.load(f)
        for item in backup_data:
            precios_backup[item['modelo']] = item
    print(f"📦 Backup cargado con {len(precios_backup)} modelos")
except FileNotFoundError:
    print("⚠️ No se encontró backup_precios.json, usando valores por defecto")

# Insertar modelos con precios del backup
for modelo in modelos:
    if modelo in precios_backup:
        backup = precios_backup[modelo]
        cursor.execute('''
            INSERT INTO precios (modelo, precio_ars, precio_usd, cotizacion, descuento, visible, dado_baja)
            VALUES (?, ?, ?, ?, ?, 1, ?)
        ''', (modelo, backup['precio_ars'], backup['precio_usd'], backup['cotizacion'], backup['descuento'], backup['dado_baja']))
    else:
        cursor.execute('''
            INSERT INTO precios (modelo, precio_ars, precio_usd, cotizacion, descuento, visible)
            VALUES (?, 0, 0, 1000, 0, 1)
        ''', (modelo,))

print(f"✅ {len(modelos)} modelos insertados con precios")

# Lista de unidades postergadas
unidades_postergadas = [
    "YAC125090007",
    "YAC125090028",
    "YAC125090029",
    "YAC125090036",
    "YAC125090046",
    "YAC125090061",
    "YAC125090079",
    "YAC125090083",
    "YAC125090097",
    "YAC125080004"
]

# Insertar unidades postergadas
for numero in unidades_postergadas:
    cursor.execute('''
        INSERT INTO unidades_postergadas (numero_fabrica)
        VALUES (?)
    ''', (numero,))

print(f"✅ {len(unidades_postergadas)} unidades postergadas insertadas")

# Insertar descuentos adicionales por defecto
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
        INSERT OR IGNORE INTO descuentos_adicionales (tipo, clave, valor)
        VALUES (?, ?, ?)
    ''', (tipo, clave, valor))

print(f"✅ {len(descuentos_default)} descuentos adicionales configurados")

# Función para asignar familia a cada modelo
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

# Actualizar familias para todos los modelos
for modelo in modelos:
    familia = obtener_familia(modelo)
    cursor.execute('UPDATE precios SET familia = ? WHERE modelo = ?', (familia, modelo))

print(f"✅ Familias asignadas a todos los modelos")

# Commit y cerrar
conn.commit()
conn.close()

print("✅ Base de datos inicializada correctamente")
print(f"📊 Total modelos: {len(modelos)}")
print(f"🚫 Total unidades postergadas: {len(unidades_postergadas)}")
print(f"🎨 Total descuentos adicionales: {len(descuentos_default)}")
