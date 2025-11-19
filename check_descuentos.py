from db_config import get_db_connection, release_db_connection

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute('SELECT modelo, descuento, descuento_futuro FROM precios ORDER BY modelo')
rows = cursor.fetchall()
release_db_connection(conn)

print("\n📊 DESCUENTOS EN LA BASE DE DATOS:\n")
print(f"{'MODELO':50} | DESC.INDIV | DESC.FUTURO")
print("-" * 80)
for r in rows:
    modelo = r['modelo'][:48]
    desc = r['descuento'] or 0
    desc_fut = r['descuento_futuro'] or 0
    print(f"{modelo:50} | {desc:8}% | {desc_fut:10}%")

print("-" * 80)
print(f"\nTOTAL: {len(rows)} modelos")
