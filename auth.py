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
    
    def __init__(self, id, username, role, full_name=None, email=None, active=True, 
                 permiso_planeamiento=False, permiso_ventas=False, 
                 permiso_gestoria=False, permiso_entregas=False):
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
    
    def get_id(self):
        return str(self.id)
    
    def is_admin(self):
        return self.role == 'admin'
    
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
            'entregas': self.permiso_entregas
        }
        
        return permissions_map.get(module, False)
    
    @staticmethod
    def get_by_id(user_id):
        """Obtener usuario por ID"""
        
        # Soporte para usuario hardcodeado
        if str(user_id) == '999999':
            hardcoded_user = User(
                id=999999,
                username='administrador',
                role='admin',
                full_name='Administrador del Sistema',
                email='admin@toyota.com',
                active=True,
                permiso_planeamiento=True,
                permiso_ventas=True,
                permiso_gestoria=True,
                permiso_entregas=True
            )
            return hardcoded_user
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, username, role, full_name, email, active,
                       permiso_planeamiento, permiso_ventas, permiso_gestoria, permiso_entregas
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
                    permiso_entregas=row['permiso_entregas']
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
        
        # 🔐 USUARIO HARDCODEADO PARA TESTING/EMERGENCIA
        # Este usuario funciona SIEMPRE, incluso si la base de datos falla
        if username == 'administrador':
            hardcoded_user = User(
                id=999999,  # ID único que no colisiona con BD
                username='administrador',
                role='admin',
                full_name='Administrador del Sistema',
                email='admin@toyota.com',
                active=True,
                permiso_planeamiento=True,
                permiso_ventas=True,
                permiso_gestoria=True,
                permiso_entregas=True
            )
            # Hash de la contraseña: LShm.2701
            hardcoded_user.password_hash = generate_password_hash('LShm.2701')
            print("⚠️  Usando usuario hardcodeado de emergencia: administrador")
            return hardcoded_user
        
        # Intentar obtener usuario de la base de datos
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, username, role, full_name, email, active, password_hash,
                       permiso_planeamiento, permiso_ventas, permiso_gestoria, permiso_entregas
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
                    permiso_entregas=row['permiso_entregas']
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


def get_all_users():
    """Obtener todos los usuarios (solo para admin)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT id, username, role, full_name, email, active, created_at, last_login,
                   permiso_planeamiento, permiso_ventas, permiso_gestoria, permiso_entregas
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
                'permiso_entregas': row['permiso_entregas']
            })
        
        return users
    except Exception as e:
        print(f"Error al obtener usuarios: {e}")
        conn.rollback()
        release_db_connection(conn)
        return []


def create_user(username, password, role='user', full_name=None, email=None,
                permiso_planeamiento=False, permiso_ventas=False, 
                permiso_gestoria=False, permiso_entregas=False):
    """Crear un nuevo usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        password_hash = generate_password_hash(password)
        
        cursor.execute('''
            INSERT INTO users (username, password_hash, role, full_name, email,
                             permiso_planeamiento, permiso_ventas, permiso_gestoria, permiso_entregas)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (username, password_hash, role, full_name, email,
              permiso_planeamiento, permiso_ventas, permiso_gestoria, permiso_entregas))
        
        user_id = cursor.fetchone()['id']
        conn.commit()
        release_db_connection(conn)
        
        return {'success': True, 'user_id': user_id}
    except Exception as e:
        conn.rollback()
        release_db_connection(conn)
        return {'success': False, 'error': str(e)}


def update_user(user_id, username=None, password=None, role=None, full_name=None, email=None, active=None,
                permiso_planeamiento=None, permiso_ventas=None, permiso_gestoria=None, permiso_entregas=None):
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
