from db_config import get_db_connection

conn = get_db_connection()
cur = conn.cursor()

# Buscar tabla de usuarios
cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
tables = [row['tablename'] for row in cur.fetchall()]
user_tables = [t for t in tables if 'user' in t.lower() or 'usuario' in t.lower()]
print("Tablas relacionadas con usuarios:", user_tables)

# Verificar columnas de la tabla usuarios
if 'users' in tables:
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'users' 
        ORDER BY ordinal_position
    """)
    print("\nColumnas de la tabla 'users':")
    for row in cur.fetchall():
        print(f"  {row['column_name']}: {row['data_type']}")

cur.close()
conn.close()
