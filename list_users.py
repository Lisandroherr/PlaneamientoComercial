"""
Script para ver todos los usuarios en la base de datos
"""

from db_config import get_db_connection, release_db_connection

def list_users():
    """Listar todos los usuarios en la base de datos"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, full_name, email, role, active, 
                   permiso_planeamiento, permiso_ventas, permiso_gestoria, permiso_entregas,
                   created_at, last_login
            FROM users 
            ORDER BY id
        ''')
        
        users = cursor.fetchall()
        release_db_connection(conn)
        
        if not users:
            print("❌ No hay usuarios en la base de datos")
            return
        
        print(f"\n{'='*80}")
        print(f"{'USUARIOS EN LA BASE DE DATOS':^80}")
        print(f"{'='*80}\n")
        
        for user in users:
            print(f"ID: {user['id']}")
            print(f"Username: {user['username']}")
            print(f"Nombre: {user['full_name'] or 'N/A'}")
            print(f"Email: {user['email']}")
            print(f"Rol: {user['role']}")
            print(f"Activo: {'✅ Sí' if user['active'] else '❌ No'}")
            print(f"Permisos:")
            print(f"  - Planeamiento: {'✅' if user['permiso_planeamiento'] else '❌'}")
            print(f"  - Ventas: {'✅' if user['permiso_ventas'] else '❌'}")
            print(f"  - Gestoría: {'✅' if user['permiso_gestoria'] else '❌'}")
            print(f"  - Entregas: {'✅' if user['permiso_entregas'] else '❌'}")
            print(f"Creado: {user['created_at']}")
            print(f"Último login: {user['last_login'] or 'Nunca'}")
            print("-" * 80)
        
        print(f"\nTotal de usuarios: {len(users)}\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    list_users()
