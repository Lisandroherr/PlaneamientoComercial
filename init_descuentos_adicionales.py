import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Crear tabla de descuentos adicionales
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

# Insertar valores por defecto
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

conn.commit()
conn.close()

print("✅ Tabla descuentos_adicionales creada e inicializada correctamente")
