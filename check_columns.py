from db_config import get_db_connection, release_db_connection

conn = get_db_connection()
cursor = conn.cursor()

cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'users' ORDER BY ordinal_position")
columns = [row['column_name'] for row in cursor.fetchall()]

print("Columnas en la tabla 'users':")
for col in columns:
    print(f"  - {col}")

release_db_connection(conn)
