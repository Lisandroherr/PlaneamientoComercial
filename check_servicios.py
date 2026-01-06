from db_config import get_db_connection

conn = get_db_connection()
cur = conn.cursor()

cur.execute('SELECT COUNT(*) as count FROM pv_servicios')
count = cur.fetchone()['count']
print(f"Total de servicios: {count}")

if count > 0:
    cur.execute('SELECT nombre, sector, ranking_comisiones FROM pv_servicios LIMIT 10')
    print("\nPrimeros 10 servicios:")
    for row in cur.fetchall():
        print(f"  - {row['nombre']} ({row['sector']}) - Ranking: {row['ranking_comisiones']}")

cur.close()
conn.close()
