from db_config import get_db_connection, release_db_connection
from auth import create_user, update_user, User

# Prueba 1: Crear un usuario con permiso_usados
print("=== Prueba 1: Crear usuario con permiso_usados ===")
result = create_user(
    username='test_usados',
    password='test123',
    role='user',
    full_name='Usuario Test Usados',
    permiso_usados=True
)
print(f"Resultado: {result}")

if result['success']:
    # Prueba 2: Verificar que el usuario tenga el permiso
    print("\n=== Prueba 2: Verificar permiso del usuario ===")
    user = User.get_by_username('test_usados')
    if user:
        print(f"Usuario: {user.username}")
        print(f"permiso_usados: {user.permiso_usados}")
        print(f"has_permission('usados'): {user.has_permission('usados')}")
        
        # Prueba 3: Actualizar el permiso
        print("\n=== Prueba 3: Actualizar permiso a False ===")
        update_result = update_user(user.id, permiso_usados=False)
        print(f"Resultado: {update_result}")
        
        # Verificar el cambio
        user_updated = User.get_by_username('test_usados')
        print(f"permiso_usados después de actualizar: {user_updated.permiso_usados}")
        
        # Prueba 4: Volver a activar el permiso
        print("\n=== Prueba 4: Volver a activar permiso ===")
        update_result2 = update_user(user.id, permiso_usados=True)
        print(f"Resultado: {update_result2}")
        
        user_final = User.get_by_username('test_usados')
        print(f"permiso_usados final: {user_final.permiso_usados}")
        
        # Limpiar
        print("\n=== Limpiando usuario de prueba ===")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username = 'test_usados'")
        conn.commit()
        release_db_connection(conn)
        print("✅ Usuario de prueba eliminado")
    else:
        print("❌ No se pudo obtener el usuario creado")
else:
    print(f"❌ Error al crear usuario: {result.get('error')}")
