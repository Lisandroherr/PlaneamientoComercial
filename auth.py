"""
Módulo de autenticación para Flask
Contiene la clase User, decoradores y funciones auxiliares
"""

from functools import wraps
from flask import redirect, url_for, flash, session
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from db_config import get_db_connection, release_db_connection
from datetime import datetime


class User(UserMixin):
    """Clase de usuario para Flask-Login"""
    
    def __init__(self, id, username, role='user', full_name=None, email=None, active=True,
                 permiso_planeamiento=False, permiso_ventas=False, 
                 permiso_gestoria=False, permiso_entregas=False, permiso_bi=False, permiso_rrhh=False, permiso_usados=False, permiso_postventa=False):
        self.id = id
        self.username = username
        self.role = role
        self.full_name = full_name
        self.email = email
        self.active = active
        self.permiso_planeamiento = permiso_planeamiento
        self.permiso_ventas = permiso_ventas
        self.permiso_gestoria = permiso_gestoria
        self.permiso_entregas = permiso_entregas
        self.permiso_bi = permiso_bi
        self.permiso_rrhh = permiso_rrhh
        self.permiso_usados = permiso_usados
        self.permiso_postventa = permiso_postventa
    
    def get_id(self):
        return str(self.id)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_usuario_plus(self):
        return self.role == 'usuario_plus'
    
    def is_usuario_plus_plus(self):
        return self.role == 'usuario_plus_plus'
    
    def is_usuario_plus_plus_plus(self):
        return self.role == 'usuario_plus_plus_plus'
    
    def is_clase_e(self):
        return self.role == 'clase_e'
    
    def is_clase_f(self):
        return self.role == 'clase_f'
    
    def is_clase_g(self):
        return self.role == 'clase_g'
    
    def has_permission(self, module):
        """Verificar si el usuario tiene permiso para acceder a un módulo"""
        # Los admins tienen acceso a todo
        if self.is_admin():
            return True
        
        # Verificar permiso específico según el módulo
        permissions_map = {
            'planeamiento': self.permiso_planeamiento,
            'ventas': self.permiso_ventas,
            'gestoria': self.permiso_gestoria,
            'entregas': self.permiso_entregas,
            'bi': self.permiso_bi,
            'rrhh': self.permiso_rrhh,
            'usados': self.permiso_usados,
            'postventa': self.permiso_postventa
        }
        
        return permissions_map.get(module, False)
    
    @staticmethod
    def get_by_id(user_id):
        """Obtener usuario por ID"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, username, role, full_name, email, active,
                       permiso_planeamiento, permiso_ventas, permiso_gestoria, permiso_entregas, permiso_bi, permiso_rrhh, permiso_usados, permiso_postventa
                FROM users
                WHERE id = %s
            ''', (user_id,))
            
            row = cursor.fetchone()
            conn.rollback()
            release_db_connection(conn)
            
            if row:
                return User(
                    id=row['id'],
                    username=row['username'],
                    role=row['role'],
                    full_name=row['full_name'],
                    email=row['email'],
                    active=row['active'],
                    permiso_planeamiento=row['permiso_planeamiento'],
                    permiso_ventas=row['permiso_ventas'],
                    permiso_gestoria=row['permiso_gestoria'],
                    permiso_entregas=row['permiso_entregas'],
                    permiso_bi=row['permiso_bi'],
                    permiso_rrhh=row['permiso_rrhh'],
                    permiso_usados=row['permiso_usados'],
                    permiso_postventa=row['permiso_postventa']
                )
            return None
        except Exception as e:
            print(f"Error al obtener usuario: {e}")
            conn.rollback()
            release_db_connection(conn)
            return None
    
    @staticmethod
    def get_by_username(username):
        """Obtener usuario por nombre de usuario"""
        
        # Obtener usuario de la base de datos
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, username, role, full_name, email, active, password_hash,
                       permiso_planeamiento, permiso_ventas, permiso_gestoria, permiso_entregas, permiso_bi, permiso_rrhh, permiso_usados, permiso_postventa
                FROM users
                WHERE username = %s
            ''', (username,))
            
            row = cursor.fetchone()
            conn.rollback()
            release_db_connection(conn)
            
            if row:
                user = User(
                    id=row['id'],
                    username=row['username'],
                    role=row['role'],
                    full_name=row['full_name'],
                    email=row['email'],
                    active=row['active'],
                    permiso_planeamiento=row['permiso_planeamiento'],
                    permiso_ventas=row['permiso_ventas'],
                    permiso_gestoria=row['permiso_gestoria'],
                    permiso_entregas=row['permiso_entregas'],
                    permiso_bi=row['permiso_bi'],
                    permiso_rrhh=row['permiso_rrhh'],
                    permiso_usados=row['permiso_usados'],
                    permiso_postventa=row['permiso_postventa']
                )
                user.password_hash = row['password_hash']
                return user
            return None
        except Exception as e:
            print(f"Error al obtener usuario: {e}")
            conn.rollback()
            release_db_connection(conn)
            return None
    
    def check_password(self, password):
        """Verificar contraseña"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Actualizar fecha de último login"""
        # Skip para usuario hardcodeado (ID 999999)
        if self.id == 999999:
            print("⚠️  Usuario hardcodeado - no se actualiza last_login en BD")
            return
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE users
                SET last_login = %s
                WHERE id = %s
            ''', (datetime.now(), self.id))
            
            conn.commit()
            release_db_connection(conn)
        except Exception as e:
            print(f"Error al actualizar last_login: {e}")
            conn.rollback()
            release_db_connection(conn)


def admin_required(f):
    """Decorador para requerir rol de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Debes iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('login'))
        
        if not current_user.is_admin():
            flash('No tienes permisos para acceder a esta página', 'danger')
            return redirect(url_for('home'))
        
        return f(*args, **kwargs)
    return decorated_function


def usuario_plus_required(f):
    """Decorador para requerir rol de Usuario + o superior"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Debes iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('login'))
        
        if not (current_user.is_admin() or current_user.is_usuario_plus()):
            flash('Necesitas permisos de Usuario + o superior para acceder a esta página', 'danger')
            return redirect(url_for('home'))
        
        return f(*args, **kwargs)
    return decorated_function


def module_permission_required(module_name):
    """Decorador para requerir permiso a un módulo específico"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Debes iniciar sesión para acceder a esta página', 'warning')
                return redirect(url_for('login'))
            
            if not current_user.has_permission(module_name):
                flash(f'No tienes permisos para acceder al módulo de {module_name.capitalize()}', 'danger')
                return redirect(url_for('home'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def usados_section_required(section):
    """Decorador para controlar acceso a secciones específicas del módulo Usados
    
    Permisos por rol:
    - Clase A (user): solo 'lavadero'
    - Clase B (usuario_plus): 'stock', 'ingresos', 'planificacion', 'lavadero', 'proveedores'
    - Clase C (usuario_plus_plus): solo 'stock' (restringido a KINTO)
    - Clase D (usuario_plus_plus_plus): solo 'stock' (restringido a TEST DRIVE)
    - Clase E: 'stock', 'ingresos', 'lavadero'
    - Clase F: 'stock', 'lavadero'
    - Clase G: 'stock', 'ingresos', 'lavadero', 'proveedores'
    - Supervisor: todas las secciones (7 módulos incluyendo proveedores)
    - Admin: todas las secciones
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Debes iniciar sesión para acceder a esta página', 'warning')
                return redirect(url_for('login'))
            
            # Admin y Supervisor tienen acceso a todo
            if current_user.role in ['admin', 'supervisor']:
                return f(*args, **kwargs)
            
            # Clase B (Usuario +) puede acceder a stock, ingresos, planificacion, lavadero, proveedores
            if current_user.role == 'usuario_plus':
                if section in ['stock', 'ingresos', 'planificacion', 'lavadero', 'proveedores']:
                    return f(*args, **kwargs)
                else:
                    flash('No tienes permisos para acceder a esta sección', 'danger')
                    return redirect(url_for('usados'))
            
            # Clase C (Usuario ++) solo puede acceder a stock (KINTO)
            if current_user.role == 'usuario_plus_plus':
                if section == 'stock':
                    return f(*args, **kwargs)
                else:
                    flash('No tienes permisos para acceder a esta sección', 'danger')
                    return redirect(url_for('usados'))
            
            # Clase D (Usuario +++) solo puede acceder a stock (TEST DRIVE)
            if current_user.role == 'usuario_plus_plus_plus':
                if section == 'stock':
                    return f(*args, **kwargs)
                else:
                    flash('No tienes permisos para acceder a esta sección', 'danger')
                    return redirect(url_for('usados'))
            
            # Clase E puede acceder a stock, ingresos, lavadero
            if current_user.role == 'clase_e':
                if section in ['stock', 'ingresos', 'lavadero']:
                    return f(*args, **kwargs)
                else:
                    flash('No tienes permisos para acceder a esta sección', 'danger')
                    return redirect(url_for('usados'))
            
            # Clase F puede acceder a stock y lavadero
            if current_user.role == 'clase_f':
                if section in ['stock', 'lavadero']:
                    return f(*args, **kwargs)
                else:
                    flash('No tienes permisos para acceder a esta sección', 'danger')
                    return redirect(url_for('usados'))
            
            # Clase G puede acceder a stock, ingresos, lavadero, proveedores
            if current_user.role == 'clase_g':
                if section in ['stock', 'ingresos', 'lavadero', 'proveedores']:
                    return f(*args, **kwargs)
                else:
                    flash('No tienes permisos para acceder a esta sección', 'danger')
                    return redirect(url_for('usados'))
            
            # Clase A (Usuario normal) solo puede acceder a lavadero
            if current_user.role == 'user':
                if section == 'lavadero':
                    return f(*args, **kwargs)
                else:
                    flash('No tienes permisos para acceder a esta sección', 'danger')
                    return redirect(url_for('usados'))
            
            # Cualquier otro caso, redirigir
            flash('No tienes permisos para acceder a esta sección', 'danger')
            return redirect(url_for('usados'))
        return decorated_function
    return decorator


def get_all_users():
    """Obtener todos los usuarios (solo para admin)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT id, username, role, full_name, email, active, created_at, last_login,
                   permiso_planeamiento, permiso_ventas, permiso_gestoria, permiso_entregas, permiso_bi, permiso_rrhh, permiso_usados, permiso_postventa
            FROM users
            ORDER BY created_at DESC
        ''')
        
        rows = cursor.fetchall()
        conn.rollback()
        release_db_connection(conn)
        
        users = []
        for row in rows:
            users.append({
                'id': row['id'],
                'username': row['username'],
                'role': row['role'],
                'full_name': row['full_name'],
                'email': row['email'],
                'active': row['active'],
                'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                'last_login': row['last_login'].isoformat() if row['last_login'] else None,
                'permiso_planeamiento': row['permiso_planeamiento'],
                'permiso_ventas': row['permiso_ventas'],
                'permiso_gestoria': row['permiso_gestoria'],
                'permiso_entregas': row['permiso_entregas'],
                'permiso_bi': row['permiso_bi'],
                'permiso_rrhh': row['permiso_rrhh'],
                'permiso_usados': row['permiso_usados'],
                'permiso_postventa': row['permiso_postventa']
            })
        
        return users
    except Exception as e:
        print(f"Error al obtener usuarios: {e}")
        conn.rollback()
        release_db_connection(conn)
        return []


def create_user(username, password, role='user', full_name=None, email=None,
                permiso_planeamiento=False, permiso_ventas=False, 
                permiso_gestoria=False, permiso_entregas=False, permiso_bi=False, permiso_rrhh=False, permiso_usados=False, permiso_postventa=False):
    """Crear un nuevo usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        password_hash = generate_password_hash(password)
        
        cursor.execute('''
            INSERT INTO users (username, password_hash, role, full_name, email,
                             permiso_planeamiento, permiso_ventas, permiso_gestoria, permiso_entregas, permiso_bi, permiso_rrhh, permiso_usados, permiso_postventa)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (username, password_hash, role, full_name, email,
              permiso_planeamiento, permiso_ventas, permiso_gestoria, permiso_entregas, permiso_bi, permiso_rrhh, permiso_usados, permiso_postventa))
        
        user_id = cursor.fetchone()['id']
        conn.commit()
        release_db_connection(conn)
        
        return {'success': True, 'user_id': user_id}
    except Exception as e:
        conn.rollback()
        release_db_connection(conn)
        return {'success': False, 'error': str(e)}


def update_user(user_id, username=None, password=None, role=None, full_name=None, email=None, active=None,
                permiso_planeamiento=None, permiso_ventas=None, permiso_gestoria=None, permiso_entregas=None,
                permiso_bi=None, permiso_rrhh=None, permiso_usados=None, permiso_postventa=None):
    """Actualizar un usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        updates = []
        params = []
        
        if username is not None:
            updates.append('username = %s')
            params.append(username)
        
        if password is not None:
            updates.append('password_hash = %s')
            params.append(generate_password_hash(password))
        
        if role is not None:
            updates.append('role = %s')
            params.append(role)
        
        if full_name is not None:
            updates.append('full_name = %s')
            params.append(full_name)
        
        if email is not None:
            updates.append('email = %s')
            params.append(email)
        
        if active is not None:
            updates.append('active = %s')
            params.append(active)
        
        if permiso_planeamiento is not None:
            updates.append('permiso_planeamiento = %s')
            params.append(permiso_planeamiento)
        
        if permiso_ventas is not None:
            updates.append('permiso_ventas = %s')
            params.append(permiso_ventas)
        
        if permiso_gestoria is not None:
            updates.append('permiso_gestoria = %s')
            params.append(permiso_gestoria)
        
        if permiso_entregas is not None:
            updates.append('permiso_entregas = %s')
            params.append(permiso_entregas)
        
        if permiso_bi is not None:
            updates.append('permiso_bi = %s')
            params.append(permiso_bi)
        
        if permiso_rrhh is not None:
            updates.append('permiso_rrhh = %s')
            params.append(permiso_rrhh)
        
        if permiso_usados is not None:
            updates.append('permiso_usados = %s')
            params.append(permiso_usados)
        
        if permiso_postventa is not None:
            updates.append('permiso_postventa = %s')
            params.append(permiso_postventa)
        
        if not updates:
            return {'success': False, 'error': 'No hay campos para actualizar'}
        
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
        
        cursor.execute(query, params)
        conn.commit()
        release_db_connection(conn)
        
        return {'success': True}
    except Exception as e:
        conn.rollback()
        release_db_connection(conn)
        return {'success': False, 'error': str(e)}


def delete_user(user_id):
    """Eliminar un usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar que no sea el único admin
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'admin' AND active = TRUE")
        admin_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT role FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if user and user['role'] == 'admin' and admin_count <= 1:
            conn.rollback()
            release_db_connection(conn)
            return {'success': False, 'error': 'No se puede eliminar el único administrador activo'}
        
        cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
        conn.commit()
        release_db_connection(conn)
        
        return {'success': True}
    except Exception as e:
        conn.rollback()
        release_db_connection(conn)
        return {'success': False, 'error': str(e)}
