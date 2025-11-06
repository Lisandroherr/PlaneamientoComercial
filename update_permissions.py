"""
Script para agregar columnas de permisos por módulo a la tabla users
Ejecutar este script UNA SOLA VEZ para actualizar la estructura de la base de datos
"""

from db_config import get_db_connection, release_db_connection
import sys

def add_permission_columns():
    """Agregar columnas de permisos a la tabla users"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("📊 Agregando columnas de permisos a la tabla users...")
        
        # Verificar si las columnas ya existen
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name IN ('permiso_planeamiento', 'permiso_ventas', 'permiso_gestoria', 'permiso_entregas')
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        if len(existing_columns) == 4:
            print("✅ Las columnas de permisos ya existen en la tabla users")
            return True
        
        # Agregar columnas de permisos (por defecto FALSE)
        columns_to_add = [
            ('permiso_planeamiento', 'BOOLEAN DEFAULT FALSE'),
            ('permiso_ventas', 'BOOLEAN DEFAULT FALSE'),
            ('permiso_gestoria', 'BOOLEAN DEFAULT FALSE'),
            ('permiso_entregas', 'BOOLEAN DEFAULT FALSE')
        ]
        
        for column_name, column_definition in columns_to_add:
            if column_name not in existing_columns:
                cursor.execute(f"""
                    ALTER TABLE users 
                    ADD COLUMN IF NOT EXISTS {column_name} {column_definition}
                """)
                print(f"   ✅ Columna '{column_name}' agregada")
        
        # Dar todos los permisos al usuario admin
        cursor.execute("""
            UPDATE users 
            SET permiso_planeamiento = TRUE,
                permiso_ventas = TRUE,
                permiso_gestoria = TRUE,
                permiso_entregas = TRUE
            WHERE role = 'admin'
        """)
        
        admin_count = cursor.rowcount
        print(f"   ✅ {admin_count} usuario(s) admin actualizado(s) con todos los permisos")
        
        conn.commit()
        print("\n✅ Base de datos actualizada correctamente")
        print("\n📋 Estructura de permisos:")
        print("   - permiso_planeamiento: Acceso al módulo de Planeamiento")
        print("   - permiso_ventas: Acceso al módulo de Ventas")
        print("   - permiso_gestoria: Acceso al módulo de Gestoría")
        print("   - permiso_entregas: Acceso al módulo de Entregas")
        print("\n💡 Los usuarios con role='admin' tienen todos los permisos habilitados automáticamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al actualizar la base de datos: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            cursor.close()
            release_db_connection(conn)

if __name__ == '__main__':
    print("=" * 60)
    print("  ACTUALIZACIÓN DE PERMISOS POR MÓDULO")
    print("=" * 60)
    print()
    
    success = add_permission_columns()
    
    if success:
        print("\n" + "=" * 60)
        print("  ✅ ACTUALIZACIÓN COMPLETADA CON ÉXITO")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("  ❌ ACTUALIZACIÓN FALLIDA")
        print("=" * 60)
        sys.exit(1)
