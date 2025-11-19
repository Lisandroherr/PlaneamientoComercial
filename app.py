from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
import pandas as pd
import os
from werkzeug.utils import secure_filename
import json
from datetime import datetime
from psycopg2 import IntegrityError as PgIntegrityError
from db_config import get_db_connection as get_pg_connection, release_db_connection, init_connection_pool
from dotenv import load_dotenv
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from auth import User, admin_required, module_permission_required, get_all_users, create_user, update_user, delete_user
from time import time

# Cargar variables de entorno
load_dotenv()

# Caché global para datos de patentamientos
patentamientos_cache = {
    'data': None,
    'timestamp': 0,
    'ttl': 1800  # 30 minutos de caché
}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'clave-secreta-por-defecto-cambiar')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Deshabilitar caché

# Inicializar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Debes iniciar sesión para acceder a esta página'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

@app.after_request
def add_header(response):
    """Agregar headers para deshabilitar caché completamente"""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# Inicializar pool de conexiones al arrancar
try:
    init_connection_pool()
    print("✅ Conexión a PostgreSQL establecida")
except Exception as e:
    print(f"❌ Error al conectar con PostgreSQL: {e}")

# Asegurar que existe la carpeta de uploads
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ==================== RUTAS DE AUTENTICACIÓN ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.get_by_username(username)
        
        if user and user.active and user.check_password(password):
            login_user(user)
            user.update_last_login()
            flash(f'Bienvenido, {user.full_name or user.username}!', 'success')
            
            # Redirigir a la página solicitada o al home
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('home'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    logout_user()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('login'))


# ==================== PANEL DE ADMINISTRACIÓN ====================

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    """Panel de gestión de usuarios (solo admin)"""
    return render_template('admin_users.html')


# API para gestión de usuarios
@app.route('/api/users', methods=['GET'])
@login_required
@admin_required
def api_get_users():
    """Obtener lista de usuarios"""
    users = get_all_users()
    return jsonify({'success': True, 'users': users})


@app.route('/api/users/<int:user_id>', methods=['GET'])
@login_required
@admin_required
def api_get_user(user_id):
    """Obtener un usuario específico"""
    user = User.get_by_id(user_id)
    if user:
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'full_name': user.full_name,
                'email': user.email,
                'active': user.active
            }
        })
    return jsonify({'success': False, 'error': 'Usuario no encontrado'}), 404


@app.route('/api/users', methods=['POST'])
@login_required
@admin_required
def api_create_user():
    """Crear un nuevo usuario"""
    data = request.json
    result = create_user(
        username=data.get('username'),
        password=data.get('password'),
        role=data.get('role', 'user'),
        full_name=data.get('full_name'),
        email=data.get('email'),
        permiso_planeamiento=data.get('permiso_planeamiento', False),
        permiso_ventas=data.get('permiso_ventas', False),
        permiso_gestoria=data.get('permiso_gestoria', False),
        permiso_entregas=data.get('permiso_entregas', False)
    )
    return jsonify(result)


@app.route('/api/users/<int:user_id>', methods=['PUT'])
@login_required
@admin_required
def api_update_user(user_id):
    """Actualizar un usuario"""
    data = request.json
    result = update_user(
        user_id=user_id,
        username=data.get('username'),
        password=data.get('password') if data.get('password') else None,
        role=data.get('role'),
        full_name=data.get('full_name'),
        email=data.get('email'),
        active=data.get('active'),
        permiso_planeamiento=data.get('permiso_planeamiento'),
        permiso_ventas=data.get('permiso_ventas'),
        permiso_gestoria=data.get('permiso_gestoria'),
        permiso_entregas=data.get('permiso_entregas')
    )
    return jsonify(result)


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
@admin_required
def api_delete_user(user_id):
    """Eliminar un usuario"""
    if user_id == current_user.id:
        return jsonify({'success': False, 'error': 'No puedes eliminar tu propio usuario'}), 400
    
    result = delete_user(user_id)
    return jsonify(result)


# ==================== RUTAS PRINCIPALES ====================

# Ruta raíz: redirigir a login si no está autenticado, o a home si ya lo está
@app.route('/')
def index():
    """Ruta raíz - redirige según estado de autenticación"""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

# Página de inicio (selector de aplicaciones)
@app.route('/home')
@login_required
def home():
    return render_template('home.html')

# Aplicación PLANEAMIENTO (requiere permiso)
@app.route('/planeamiento')
@login_required
@module_permission_required('planeamiento')
def planeamiento():
    return render_template('planeamiento.html')

# Aplicación VENTAS
@app.route('/ventas')
@login_required
@module_permission_required('ventas')
def ventas():
    return render_template('ventas.html')

# Aplicación ENTREGAS
@app.route('/entregas')
@login_required
@module_permission_required('entregas')
def entregas():
    return render_template('entregas.html')

@app.route('/entregas/reportes')
@login_required
@module_permission_required('entregas')
def entregas_reportes():
    return render_template('entregas_reportes.html')


# ==================== BUSINESS INTELLIGENCE ANALYSIS ====================

@app.route('/bi_analysis')
@login_required
def bi_analysis():
    """Página principal de Business Intelligence Analysis"""
    return render_template('bi_analysis.html')

@app.route('/bi/bases_datos')
@login_required
def bi_bases_datos():
    """Módulo de carga de bases de datos"""
    return render_template('bi_bases_datos.html')

@app.route('/bi/patentamientos')
@login_required
def bi_patentamientos():
    """Módulo de análisis de patentamientos"""
    return render_template('bi_patentamientos.html')

@app.route('/bi/entregas')
@login_required
def bi_entregas():
    """Módulo de análisis de entregas y plan de negocio"""
    return render_template('bi_entregas.html')

@app.route('/bi/recaudacion')
@login_required
def bi_recaudacion():
    """Módulo de análisis de recaudación (en construcción)"""
    return render_template('bi_recaudacion.html')


# ==================== FUNCIONES DE BASE DE DATOS ====================

def get_db_connection():
    """Crear conexión a la base de datos PostgreSQL"""
    return get_pg_connection()


# Módulo 1: Lista de precios
@app.route('/modulo1')
@login_required
@module_permission_required('planeamiento')
def modulo1():
    return render_template('modulo1.html')

# API para obtener precios
@app.route('/api/precios', methods=['GET'])
@login_required
@module_permission_required('planeamiento')
def get_precios():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT modelo, precio_ars, precio_usd, cotizacion, descuento, descuento_futuro, visible, dado_baja, familia FROM precios ORDER BY familia, modelo')
    rows = cursor.fetchall()
    conn.rollback()
    release_db_connection(conn)
    
    modelos = []
    modelos_ocultos = []
    
    for row in rows:
        modelo_data = {
            'nombre': row['modelo'],
            'precio_ars': row['precio_ars'],
            'precio_usd': row['precio_usd'],
            'cotizacion': row['cotizacion'],
            'descuento': row['descuento'],
            'descuento_futuro': row.get('descuento_futuro', 0) or 0,
            'dado_baja': row['dado_baja'],
            'familia': row['familia'] or 'OTROS'
        }
        modelos.append(modelo_data)
        
        if row['visible'] == 0:
            modelos_ocultos.append(row['modelo'])
    
    return jsonify({
        'modelos': modelos,
        'modelos_ocultos': modelos_ocultos
    })

# API para guardar precios
@app.route('/api/precios', methods=['POST'])
@login_required
@module_permission_required('planeamiento')
def save_precios():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Actualizar precios de TODOS los modelos (convencionales y SC)
        for modelo in data.get('modelos', []):
            cursor.execute('''
                UPDATE precios 
                SET precio_ars = %s, precio_usd = %s, cotizacion = %s, descuento = %s, descuento_futuro = %s, dado_baja = %s, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE modelo = %s
            ''', (modelo['precio_ars'], modelo['precio_usd'], modelo['cotizacion'], modelo['descuento'], modelo.get('descuento_futuro', 0), modelo.get('dado_baja', 0), modelo['nombre']))
        
        # Actualizar visibilidad
        # Primero poner todos como visibles
        cursor.execute('UPDATE precios SET visible = 1')
        
        # Luego ocultar los que están en la lista
        for modelo_oculto in data.get('modelos_ocultos', []):
            cursor.execute('UPDATE precios SET visible = 0 WHERE modelo = %s', (modelo_oculto,))
        
        conn.commit()
        release_db_connection(conn)
        
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        release_db_connection(conn)
        return jsonify({'success': False, 'error': str(e)}), 500

# API para aplicar descuento por familia
@app.route('/api/descuento_familia', methods=['POST'])
@login_required
@module_permission_required('planeamiento')
def aplicar_descuento_familia():
    data = request.json
    familia = data.get('familia')
    descuento = data.get('descuento', 0)
    
    if not familia:
        return jsonify({'success': False, 'error': 'Familia no especificada'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Contar modelos afectados
        cursor.execute('SELECT COUNT(*) as total FROM precios WHERE familia = %s', (familia,))
        total = cursor.fetchone()['total']
        
        # Aplicar descuento
        cursor.execute('UPDATE precios SET descuento = %s WHERE familia = %s', (descuento, familia))
        conn.commit()
        release_db_connection(conn)
        
        return jsonify({'success': True, 'modelos_actualizados': total})
    except Exception as e:
        conn.rollback()
        release_db_connection(conn)
        return jsonify({'success': False, 'error': str(e)}), 500

# API para obtener descuentos adicionales
@app.route('/api/descuentos_adicionales', methods=['GET'])
@login_required
@module_permission_required('planeamiento')
def get_descuentos_adicionales():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT tipo, clave, valor FROM descuentos_adicionales')
    rows = cursor.fetchall()
    release_db_connection(conn)
    
    descuentos = {}
    for row in rows:
        if row['tipo'] not in descuentos:
            descuentos[row['tipo']] = {}
        descuentos[row['tipo']][row['clave']] = row['valor']
    
    return jsonify(descuentos)

# API para guardar descuentos adicionales
@app.route('/api/descuentos_adicionales', methods=['POST'])
@login_required
@module_permission_required('planeamiento')
def save_descuentos_adicionales():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for tipo, valores in data.items():
            for clave, valor in valores.items():
                cursor.execute('''
                    INSERT INTO descuentos_adicionales (tipo, clave, valor, fecha_actualizacion)
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (tipo, clave) 
                    DO UPDATE SET valor = EXCLUDED.valor, fecha_actualizacion = CURRENT_TIMESTAMP
                ''', (tipo, clave, valor))
        
        conn.commit()
        release_db_connection(conn)
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        release_db_connection(conn)
        return jsonify({'success': False, 'error': str(e)}), 500

# API para obtener unidades postergadas
@app.route('/api/unidades_postergadas', methods=['GET'])
@login_required
@module_permission_required('planeamiento')
def get_unidades_postergadas():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT numero_fabrica FROM unidades_postergadas ORDER BY fecha_agregado DESC')
    rows = cursor.fetchall()
    release_db_connection(conn)
    
    unidades = [row['numero_fabrica'] for row in rows]
    return jsonify(unidades)

# API para agregar unidad postergada
@app.route('/api/unidades_postergadas', methods=['POST'])
@login_required
@module_permission_required('planeamiento')
def add_unidad_postergada():
    data = request.json
    numero_fabrica = data.get('numero_fabrica', '').strip()
    
    if not numero_fabrica:
        return jsonify({'success': False, 'error': 'Número de fábrica vacío'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT INTO unidades_postergadas (numero_fabrica) VALUES (%s)', (numero_fabrica,))
        conn.commit()
        release_db_connection(conn)
        return jsonify({'success': True})
    except PgIntegrityError:
        conn.rollback()
        release_db_connection(conn)
        return jsonify({'success': False, 'error': 'Número de fábrica ya existe'}), 400
    except Exception as e:
        conn.rollback()
        release_db_connection(conn)
        return jsonify({'success': False, 'error': str(e)}), 500

# API para eliminar unidad postergada
@app.route('/api/unidades_postergadas/<numero_fabrica>', methods=['DELETE'])
@login_required
@module_permission_required('planeamiento')
def delete_unidad_postergada(numero_fabrica):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM unidades_postergadas WHERE numero_fabrica = %s', (numero_fabrica,))
        conn.commit()
        release_db_connection(conn)
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        release_db_connection(conn)
        return jsonify({'success': False, 'error': str(e)}), 500


# Módulo 2: Tabla editable (a desarrollar)
@app.route('/modulo2')
@login_required
@module_permission_required('planeamiento')
def modulo2():
    return render_template('modulo2.html')


# ==================== API MÓDULO 2: PREVENTA ====================

# API para obtener preventa
@app.route('/api/preventa', methods=['GET'])
@login_required
@module_permission_required('planeamiento')
def get_preventa():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, numero_fabrica, modelo_version, operacion, vendedor, color, informado, cancelado, asignado 
        FROM preventa 
        ORDER BY id ASC
    ''')
    rows = cursor.fetchall()
    release_db_connection(conn)
    
    preventa = []
    for row in rows:
        preventa.append({
            'id': row['id'],
            'numero_fabrica': row['numero_fabrica'],
            'modelo_version': row['modelo_version'],
            'operacion': row['operacion'],
            'vendedor': row['vendedor'],
            'color': row['color'],
            'informado': row['informado'],
            'cancelado': row['cancelado'],
            'asignado': row['asignado']
        })
    
    return jsonify(preventa)

# API para guardar/actualizar preventa (reemplaza toda la tabla)
@app.route('/api/preventa', methods=['POST'])
@login_required
@module_permission_required('planeamiento')
def save_preventa():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Paso 1: Eliminar TODAS las unidades de preventa del módulo disponible
        # Esto asegura que si la bitácora se limpia, el disponible también se limpia
        cursor.execute('''
            DELETE FROM disponibles 
            WHERE numero_fabrica = 'YAC999999999'
        ''')
        print(f"🗑️ Unidades de preventa eliminadas del disponible")
        
        # Paso 2: Eliminar todos los registros de preventa
        cursor.execute('DELETE FROM preventa')
        
        # Paso 3: Insertar nuevos registros (solo si hay datos)
        if len(data) > 0:
            for item in data:
                cursor.execute('''
                    INSERT INTO preventa (
                        numero_fabrica, modelo_version, operacion, vendedor, color, informado, cancelado, asignado
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    'YAC999999999',  # Número de fábrica fijo para preventa
                    item.get('modelo_version', ''),
                    item.get('operacion', ''),
                    item.get('vendedor', ''),
                    item.get('color', ''),
                    1 if item.get('informado') else 0,
                    1 if item.get('cancelado') else 0,
                    1 if item.get('asignado') else 0
                ))
        
        conn.commit()
        release_db_connection(conn)
        
        return jsonify({'success': True, 'count': len(data), 'message': 'Bitácora guardada y disponible actualizado'})
    except Exception as e:
        conn.rollback()
        release_db_connection(conn)
        return jsonify({'success': False, 'error': str(e)}), 500

# API para convertir preventa sin vendedor a disponible
@app.route('/api/preventa/convertir_disponible', methods=['POST'])
@login_required
@module_permission_required('planeamiento')
def convertir_preventa_disponible():
    """Convierte unidades de preventa SIN vendedor al módulo disponible"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Paso 1: Limpiar TODAS las unidades de preventa anteriores del disponible
        cursor.execute('''
            DELETE FROM disponibles 
            WHERE numero_fabrica = 'YAC999999999'
        ''')
        print(f"🗑️ Limpieza: Unidades de preventa anteriores eliminadas del disponible")
        
        # Paso 2: Obtener registros de preventa sin vendedor asignado
        cursor.execute('''
            SELECT numero_fabrica, modelo_version, operacion, color
            FROM preventa
            WHERE vendedor IS NULL OR vendedor = ''
        ''')
        preventas = cursor.fetchall()
        
        if len(preventas) == 0:
            conn.commit()  # Confirmar la limpieza aunque no haya nada que agregar
            release_db_connection(conn)
            return jsonify({'success': True, 'count': 0, 'message': 'No hay unidades sin vendedor. Preventa anterior limpiada del disponible.'})
        
        # Calcular fecha de entrega estimada (3 meses adelante)
        from datetime import datetime, timedelta
        fecha_entrega = datetime.now() + timedelta(days=90)  # 3 meses
        fecha_entrega_str = fecha_entrega.strftime('%Y-%m-%d')
        
        # Obtener precios de la base de datos
        cursor.execute('SELECT modelo, precio_ars, descuento FROM precios')
        precios_data = {}
        for row in cursor.fetchall():
            precios_data[row['modelo']] = {
                'precio_ars': row['precio_ars'],
                'descuento': row['descuento']
            }
        
        # Insertar en disponibles
        count = 0
        for prev in preventas:
            modelo = prev['modelo_version']
            
            # Obtener precio BASE (sin descuento)
            # Los descuentos se aplicarán en el Módulo 4
            precio = 0
            if modelo in precios_data:
                precio = precios_data[modelo]['precio_ars']
            
            cursor.execute('''
                INSERT INTO disponibles (
                    numero_fabrica, modelo_version, color, ubicacion, 
                    entrega_estimada, precio_disponible, operacion
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (
                prev['numero_fabrica'],  # Usar el número de fábrica de preventa (YAC999999999)
                modelo,
                prev['color'],
                "Preventa",
                fecha_entrega_str,
                precio,
                prev['operacion']
            ))
            count += 1
        
        conn.commit()
        release_db_connection(conn)
        
        return jsonify({'success': True, 'count': count, 'message': f'{count} unidades de preventa agregadas a disponible'})
    except Exception as e:
        conn.rollback()
        release_db_connection(conn)
        return jsonify({'success': False, 'error': str(e)}), 500


# Módulo 3: Procesador de Excel
@app.route('/modulo3')
@login_required
@module_permission_required('planeamiento')
def modulo3():
    return render_template('modulo3.html')


@app.route('/procesar_excel', methods=['POST'])
@login_required
@module_permission_required('planeamiento')
def procesar_excel():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No se encontró ningún archivo'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Tipo de archivo no permitido. Use .xlsx o .xls'}), 400
        
        # Obtener lista de unidades postergadas desde la base de datos
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT numero_fabrica FROM unidades_postergadas')
        rows = cursor.fetchall()
        release_db_connection(conn)
        
        unidades_postergadas = [row['numero_fabrica'] for row in rows]
        print(f"Unidades postergadas desde BD: {unidades_postergadas}")
        
        # Guardar archivo temporalmente
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Debug: verificar permisos y ruta
        print(f"📁 Intentando guardar en: {filepath}")
        print(f"📁 Directorio uploads existe: {os.path.exists(app.config['UPLOAD_FOLDER'])}")
        print(f"📁 Permisos del directorio: {oct(os.stat(app.config['UPLOAD_FOLDER']).st_mode)}")
        
        try:
            file.save(filepath)
            print(f"✅ Archivo guardado exitosamente en {filepath}")
        except Exception as save_error:
            print(f"❌ Error al guardar archivo: {save_error}")
            return jsonify({'error': f'Error al guardar archivo: {str(save_error)}'}), 500
        
        # Leer el archivo Excel
        df = pd.read_excel(filepath, header=None)
        
        # Paso 1: Eliminar las primeras 8 filas
        df = df.iloc[8:]
        
        # Paso 2: Eliminar la columna C (índice 2, ya que comienza en 0)
        if df.shape[1] > 2:  # Verificar que existe la columna C
            df = df.drop(df.columns[2], axis=1)
        
        # Paso 3: Eliminar filas completamente vacías
        df = df.dropna(how='all')
        
        # Paso 4: Ordenar por la primera columna (columna A)
        df = df.sort_values(by=df.columns[0], ascending=True)
        
        # Resetear el índice
        df = df.reset_index(drop=True)
        
        # Nombres de las columnas (primeras 15 columnas visibles)
        column_names = [
            'Nº Fábrica', 'Nº Chasis', 'Modelo/Versión', 'Color', 
            'Fecha Finanzas', 'Despacho Estimado', 'Entrega Estimada',
            'Fecha Recepción', 'Ubicación', 'Días Stock', 'Precio p/ Disponible',
            'Cód. Cliente', 'Cliente', 'Vendedor', 'Operación'
        ]
        
        # Asignar nombres a las primeras 15 columnas
        for i in range(min(15, len(df.columns))):
            df.rename(columns={df.columns[i]: column_names[i]}, inplace=True)
        
        # Calcular "Entrega Estimada" = "Despacho Estimado" + 1 mes
        if 'Despacho Estimado' in df.columns:
            # Convertir a datetime manejando errores
            df['Despacho Estimado'] = pd.to_datetime(df['Despacho Estimado'], errors='coerce')
            
            # Rellenar valores vacíos con 31/12/2030
            fecha_default = pd.Timestamp('2030-12-31')
            df['Despacho Estimado'] = df['Despacho Estimado'].fillna(fecha_default)
            
            # Calcular Entrega Estimada sumando 1 mes
            df['Entrega Estimada'] = df['Despacho Estimado'] + pd.DateOffset(months=1)
        
        # **NUEVO: Obtener precios de la base de datos y hacer match con Modelo/Versión ANTES DE CORTAR**
        if 'Modelo/Versión' in df.columns and 'Precio p/ Disponible' in df.columns:
            print("🔄 Haciendo match de precios desde la base de datos...")
            
            # Obtener todos los precios, descuentos individuales y descuentos futuros de la base de datos
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT modelo, precio_ars, descuento, descuento_futuro FROM precios')
            precios_data = {}
            for row in cursor.fetchall():
                modelo = row['modelo']
                precio_ars = row['precio_ars'] or 0
                descuento = row['descuento'] or 0
                descuento_futuro = row.get('descuento_futuro', 0) or 0
                
                precios_data[modelo] = {
                    'precio_ars': precio_ars,
                    'descuento': descuento,
                    'descuento_futuro': descuento_futuro
                }
                
                print(f"🔧 Cargado: {modelo[:40]:40} | Precio: ${precio_ars:,.0f} | Desc: {descuento}% | Desc.Futuro: {descuento_futuro}%")
            
            conn.rollback()
            release_db_connection(conn)
            
            print(f"📊 Precios cargados: {len(precios_data)} modelos")
            
            # Obtener fecha actual para comparar
            from datetime import datetime
            hoy = datetime.now()
            hoy_ym = (hoy.year, hoy.month)
            
            # Aplicar precio con descuento según fecha de DESPACHO
            def calcular_precio_con_descuento(row):
                modelo = row['Modelo/Versión']
                despacho_estimado = row['Despacho Estimado']
                numero_fabrica = row.get('Nº Fábrica', 'N/A')
                
                if pd.isna(modelo):
                    print(f"⚠️ Modelo vacío, saltando...")
                    return pd.Series({
                        'Precio p/ Disponible': 0,
                        'Precio Base': 0,
                        'Descuento Aplicado (%)': 0
                    })
                
                modelo_str = str(modelo).strip()
                
                # Buscar coincidencia exacta
                if modelo_str not in precios_data:
                    print(f"⚠️ Modelo '{modelo_str}' NO encontrado en precios_data")
                    return pd.Series({
                        'Precio p/ Disponible': 0,
                        'Precio Base': 0,
                        'Descuento Aplicado (%)': 0
                    })
                
                precio_base = precios_data[modelo_str]['precio_ars']
                descuento_individual = precios_data[modelo_str]['descuento']
                descuento_futuro = precios_data[modelo_str]['descuento_futuro']
                
                print(f"🔍 {modelo_str[:40]:40} | Nº Fábrica: {numero_fabrica}")
                print(f"   Precio Base: ${precio_base:,.0f}")
                print(f"   Desc Individual: {descuento_individual}%")
                print(f"   Desc Futuro: {descuento_futuro}%")
                
                # Determinar si es mes futuro o actual BASADO EN DESPACHO ESTIMADO
                es_mes_actual_o_futuro = False
                if not pd.isna(despacho_estimado):
                    try:
                        if isinstance(despacho_estimado, str):
                            fecha_despacho = pd.to_datetime(despacho_estimado)
                        else:
                            fecha_despacho = despacho_estimado
                        
                        despacho_ym = (fecha_despacho.year, fecha_despacho.month)
                        
                        print(f"   Fecha Despacho: {despacho_ym} vs Hoy: {hoy_ym}")
                        
                        # Solo meses FUTUROS usan descuento_futuro (mes actual usa descuento_individual)
                        if despacho_ym > hoy_ym:
                            es_mes_actual_o_futuro = True
                            print(f"   ✅ MES FUTURO -> usando descuento_futuro")
                        else:
                            print(f"   ⏸️ MES ACTUAL O ANTERIOR -> usando descuento_individual")
                    except Exception as e:
                        print(f"   ⚠️ Error procesando fecha: {e}")
                        pass
                
                # Aplicar el descuento correspondiente
                descuento_aplicar = descuento_futuro if es_mes_actual_o_futuro else descuento_individual
                
                # Calcular precio final
                precio_final = precio_base * (1 - descuento_aplicar / 100)
                
                print(f"   💰 Descuento aplicado: {descuento_aplicar}% -> Precio Final: ${precio_final:,.0f}")
                print("")
                
                return pd.Series({
                    'Precio p/ Disponible': precio_final,
                    'Precio Base': precio_base,
                    'Descuento Aplicado (%)': descuento_aplicar
                })
            
            # Aplicar la función y crear las tres columnas
            resultado = df.apply(calcular_precio_con_descuento, axis=1)
            df['Precio p/ Disponible'] = resultado['Precio p/ Disponible']
            df['Precio Base'] = resultado['Precio Base']
            df['Descuento Aplicado (%)'] = resultado['Descuento Aplicado (%)']
            
            # Contar cuántos precios se encontraron
            precios_encontrados = (df['Precio p/ Disponible'] > 0).sum()
            print(f"✅ Precios con descuento aplicados: {precios_encontrados} de {len(df)} registros")
        
        # Mantener solo las 15 columnas originales + 3 nuevas (18 total)
        # Orden: 0-14 (originales) + 15,16,17 (Precio p/ Disponible, Precio Base, Descuento Aplicado)
        columnas_a_mantener = [
            'Nº Fábrica', 'Nº Chasis', 'Modelo/Versión', 'Color', 
            'Fecha Finanzas', 'Despacho Estimado', 'Entrega Estimada',
            'Fecha Recepción', 'Ubicación', 'Días Stock', 'Precio p/ Disponible',
            'Cód. Cliente', 'Cliente', 'Vendedor', 'Operación',
            'Precio Base', 'Descuento Aplicado (%)'
        ]
        # Solo mantener las columnas que existen
        columnas_existentes = [col for col in columnas_a_mantener if col in df.columns]
        df = df[columnas_existentes]
        
        print(f"📊 Columnas finales del DataFrame: {list(df.columns)}")
        
        # **Filtrar unidades postergadas ANTES de dividir por pestañas**
        if unidades_postergadas and 'Nº Fábrica' in df.columns:
            filas_antes = len(df)
            # Convertir Nº Fábrica a string y eliminar espacios
            df['Nº Fábrica'] = df['Nº Fábrica'].astype(str).str.strip()
            # Filtrar las filas que NO estén en la lista de postergadas
            df = df[~df['Nº Fábrica'].isin(unidades_postergadas)]
            filas_despues = len(df)
            print(f"Filtrado de unidades postergadas: {filas_antes} filas -> {filas_despues} filas ({filas_antes - filas_despues} eliminadas)")
        
        # Convertir la primera columna a string para el análisis de prefijos
        df['Nº Fábrica'] = df['Nº Fábrica'].astype(str)
        
        # Separar por tipo de canal de venta según el prefijo de "Nº Fábrica"
        tabs_data = []
        
        # Ventas Especiales (F)
        df_ventas_especiales = df[df['Nº Fábrica'].str.startswith('F', na=False)].copy()
        if not df_ventas_especiales.empty:
            tabs_data.append({
                'id': 'ventas-especiales',
                'name': 'Ventas Especiales (F)',
                'count': len(df_ventas_especiales),
                'columns': list(df_ventas_especiales.columns),
                'rows': df_ventas_especiales.where(pd.notnull(df_ventas_especiales), None).values.tolist()
            })
        
        # Plan de Ahorro (TPA)
        df_plan_ahorro = df[df['Nº Fábrica'].str.startswith('TPA', na=False)].copy()
        if not df_plan_ahorro.empty:
            tabs_data.append({
                'id': 'plan-ahorro',
                'name': 'Plan de Ahorro (TPA)',
                'count': len(df_plan_ahorro),
                'columns': list(df_plan_ahorro.columns),
                'rows': df_plan_ahorro.where(pd.notnull(df_plan_ahorro), None).values.tolist()
            })
        
        # Ventas Convencionales (YAC)
        df_ventas_convencionales = df[df['Nº Fábrica'].str.startswith('YAC', na=False)].copy()
        if not df_ventas_convencionales.empty:
            tabs_data.append({
                'id': 'ventas-convencionales',
                'name': 'Ventas Convencionales (YAC)',
                'count': len(df_ventas_convencionales),
                'columns': list(df_ventas_convencionales.columns),
                'rows': df_ventas_convencionales.where(pd.notnull(df_ventas_convencionales), None).values.tolist()
            })
        
        # No incluir la pestaña "Otros" - comentado para simplificar
        # df_otros = df[~df['Nº Fábrica'].str.match(r'^(F|TPA|YAC)', na=False)].copy()
        
        # Eliminar archivo temporal
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'tabs': tabs_data,
            'total_rows': len(df)
        })
    
    except Exception as e:
        # Limpiar archivo si existe
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': f'Error al procesar el archivo: {str(e)}'}), 500


# Módulos 4, 5 y 6 (placeholders)
@app.route('/modulo4')
@login_required
@module_permission_required('planeamiento')
def modulo4():
    return render_template('modulo4.html')


@app.route('/modulo5')
@login_required
@module_permission_required('planeamiento')
def modulo5():
    return render_template('modulo5.html')


@app.route('/modulo6')
@login_required
@module_permission_required('planeamiento')
def modulo6():
    return render_template('modulo6.html')


# ==================== API MÓDULO 4: DISPONIBLES ====================

# API para obtener unidades disponibles
@app.route('/api/disponibles', methods=['GET'])
@login_required
def get_disponibles():
    # Verificar que tenga permiso de planeamiento O ventas
    if not (current_user.has_permission('planeamiento') or current_user.has_permission('ventas')):
        return jsonify({'error': 'No tienes permisos para acceder a esta información'}), 403
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Obtener descuentos adicionales
    cursor.execute('SELECT tipo, clave, valor FROM descuentos_adicionales')
    desc_rows = cursor.fetchall()
    descuentos_config = {}
    for row in desc_rows:
        if row['tipo'] not in descuentos_config:
            descuentos_config[row['tipo']] = {}
        descuentos_config[row['tipo']][row['clave']] = row['valor']
    
    cursor.execute('''
        SELECT d.numero_fabrica, d.numero_chasis, d.modelo_version, d.color,
               d.fecha_finanzas, d.despacho_estimado, d.entrega_estimada,
               d.fecha_recepcion, d.ubicacion, d.dias_stock, d.precio_disponible,
               d.cod_cliente, d.cliente, d.vendedor, d.operacion,
               d.precio_base, d.descuento_individual as descuento_guardado, d.descuento_adicional,
               p.familia, p.descuento as descuento_individual, p.descuento_futuro
        FROM disponibles d
        LEFT JOIN precios p ON d.modelo_version = p.modelo
        ORDER BY d.fecha_carga DESC
    ''')
    rows = cursor.fetchall()
    conn.rollback()
    release_db_connection(conn)
    
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    
    disponibles = []
    for row in rows:
        # Usar el precio_base guardado o el precio_disponible como fallback
        precio_base_guardado = row.get('precio_base', 0) or row['precio_disponible'] or 0
        
        # Usar el descuento individual que ya fue guardado al procesar el Excel
        descuento_individual_guardado = row.get('descuento_guardado', 0) or 0
        
        descuento_total = descuento_individual_guardado
        detalles_descuento = []
        
        # Determinar fecha de entrega para calcular descuentos adicionales
        fecha_entrega_parsed = None
        
        if row['entrega_estimada']:
            try:
                fecha_str = str(row['entrega_estimada'])
                # Intentar parsear la fecha
                try:
                    fecha_entrega_parsed = datetime.strptime(fecha_str, '%Y-%m-%d')
                except:
                    try:
                        if 'GMT' in fecha_str:
                            fecha_str_limpia = fecha_str.replace(' GMT', '').strip()
                            fecha_entrega_parsed = datetime.strptime(fecha_str_limpia, '%a, %d %b %Y %H:%M:%S')
                        else:
                            fecha_entrega_parsed = datetime.fromisoformat(fecha_str.replace('GMT', '').strip())
                    except:
                        pass
            except Exception as e:
                pass
        
        # Descuento por Stock
        ubicacion_actual = (row['ubicacion'] or '').strip().upper()
        desc_stock = descuentos_config.get('stock', {}).get('descuento_stock', 0)
        
        # Comparar si contiene "STOCK" en cualquier parte
        if 'STOCK' in ubicacion_actual and desc_stock > 0:
            descuento_total += desc_stock
            detalles_descuento.append(f"Stock: {desc_stock}%")
        
        # Descuento por Color - Normalizar para comparar
        color_original = (row['color'] or '').strip()
        color_normalizado = color_original.lower().replace(' ', '_')
        desc_color = descuentos_config.get('color', {}).get(color_normalizado, 0)
        if desc_color > 0:
            descuento_total += desc_color
            detalles_descuento.append(f"Color: {desc_color}%")
        
        # Descuento por Antigüedad
        if fecha_entrega_parsed:
            try:
                meses_config = descuentos_config.get('antiguedad', {}).get('meses', 3)
                desc_antiguedad = descuentos_config.get('antiguedad', {}).get('descuento', 0)
                fecha_limite = datetime.now() - relativedelta(months=int(meses_config))
                
                if fecha_entrega_parsed < fecha_limite and desc_antiguedad > 0:
                    descuento_total += desc_antiguedad
                    detalles_descuento.append(f"Antigüedad: {desc_antiguedad}%")
            except Exception as e:
                print(f"❌ Error procesando antigüedad para {row['numero_fabrica']}: {e}")
        
        # Calcular precio final con TODOS los descuentos
        precio_final = precio_base_guardado * (1 - descuento_total / 100)
        
        # Separar descuento individual (va en su propia columna) del total de adicionales
        descuento_adicional = descuento_total - descuento_individual_guardado
        
        disponibles.append({
            'numero_fabrica': row['numero_fabrica'],
            'numero_chasis': row['numero_chasis'],
            'modelo_version': row['modelo_version'],
            'color': row['color'],
            'fecha_finanzas': row['fecha_finanzas'],
            'despacho_estimado': row['despacho_estimado'],
            'entrega_estimada': row['entrega_estimada'],
            'fecha_recepcion': row['fecha_recepcion'],
            'ubicacion': row['ubicacion'],
            'dias_stock': row['dias_stock'],
            'precio_disponible': round(precio_final, 2),
            'precio_base': precio_base_guardado,
            'descuento_individual': descuento_individual_guardado,
            'descuento_adicional': round(descuento_adicional, 2),
            'detalles_descuento': ', '.join(detalles_descuento) if detalles_descuento else 'Sin descuentos',
            'cod_cliente': row['cod_cliente'],
            'cliente': row['cliente'],
            'vendedor': row['vendedor'],
            'operacion': row['operacion'],
            'familia': row['familia'] or 'SIN FAMILIA'
        })
    
    # DEBUG: Mostrar qué se está enviando al frontend
    print(f"\n🚀 ============ ENVIANDO DATOS AL FRONTEND (MÓDULO 4) ============")
    print(f"   Total de unidades: {len(disponibles)}")
    if len(disponibles) > 0:
        print(f"\n   📤 Primera unidad que se envía:")
        print(f"      Nº Fábrica: {disponibles[0]['numero_fabrica']}")
        print(f"      Modelo: {disponibles[0]['modelo_version']}")
        print(f"      Precio Base: ${disponibles[0]['precio_base']}")
        print(f"      Descuento Individual: {disponibles[0]['descuento_individual']}%")
        print(f"      Descuento Adicional: {disponibles[0]['descuento_adicional']}%")
        print(f"      Precio Final: ${disponibles[0]['precio_disponible']}")
        
        if len(disponibles) > 1:
            print(f"\n   📤 Segunda unidad que se envía:")
            print(f"      Nº Fábrica: {disponibles[1]['numero_fabrica']}")
            print(f"      Modelo: {disponibles[1]['modelo_version']}")
            print(f"      Descuento Individual: {disponibles[1]['descuento_individual']}%")
        
        if len(disponibles) > 2:
            print(f"\n   📤 Tercera unidad que se envía:")
            print(f"      Nº Fábrica: {disponibles[2]['numero_fabrica']}")
            print(f"      Modelo: {disponibles[2]['modelo_version']}")
            print(f"      Descuento Individual: {disponibles[2]['descuento_individual']}%")
    print(f"   ==================================================================\n")
    
    return jsonify(disponibles)

# API para guardar/reemplazar unidades disponibles
@app.route('/api/disponibles', methods=['POST'])
@login_required
@module_permission_required('planeamiento')
def save_disponibles():
    data = request.json
    
    print(f"\n🔍 ============ RECIBIENDO DATOS PARA GUARDAR EN DISPONIBLES ============")
    print(f"   Total de unidades: {len(data)}")
    if len(data) > 0:
        print(f"\n   📦 Primera unidad recibida:")
        print(f"      Nº Fábrica: {data[0].get('numero_fabrica')}")
        print(f"      Modelo: {data[0].get('modelo_version')}")
        print(f"      Precio Disponible: {data[0].get('precio_disponible')}")
        print(f"      Precio Base: {data[0].get('precio_base')}")
        print(f"      Descuento Aplicado: {data[0].get('descuento_aplicado')} %")
        print(f"\n   🔑 TODAS las claves disponibles: {list(data[0].keys())}")
        
        # Mostrar más unidades para verificar el patrón
        if len(data) > 1:
            print(f"\n   📦 Segunda unidad recibida:")
            print(f"      Nº Fábrica: {data[1].get('numero_fabrica')}")
            print(f"      Modelo: {data[1].get('modelo_version')}")
            print(f"      Descuento Aplicado: {data[1].get('descuento_aplicado')} %")
        
        if len(data) > 2:
            print(f"\n   📦 Tercera unidad recibida:")
            print(f"      Nº Fábrica: {data[2].get('numero_fabrica')}")
            print(f"      Modelo: {data[2].get('modelo_version')}")
            print(f"      Descuento Aplicado: {data[2].get('descuento_aplicado')} %")
    print(f"   ========================================================================\n")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Eliminar todos los registros anteriores
        cursor.execute('DELETE FROM disponibles')
        
        # Insertar nuevos registros
        for item in data:
            cursor.execute('''
                INSERT INTO disponibles (
                    numero_fabrica, numero_chasis, modelo_version, color,
                    fecha_finanzas, despacho_estimado, entrega_estimada,
                    fecha_recepcion, ubicacion, dias_stock, precio_disponible,
                    cod_cliente, cliente, vendedor, operacion,
                    precio_base, descuento_individual, descuento_adicional
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                item.get('numero_fabrica'),
                item.get('numero_chasis'),
                item.get('modelo_version'),
                item.get('color'),
                item.get('fecha_finanzas'),
                item.get('despacho_estimado'),
                item.get('entrega_estimada'),
                item.get('fecha_recepcion'),
                item.get('ubicacion'),
                item.get('dias_stock'),
                item.get('precio_disponible'),
                item.get('cod_cliente'),
                item.get('cliente'),
                item.get('vendedor'),
                item.get('operacion'),
                item.get('precio_base', 0),
                item.get('descuento_aplicado', 0),  # Este es el descuento individual que se aplicó
                0  # descuento_adicional se calculará en Módulo 4
            ))
        
        conn.commit()
        conn.rollback()
        release_db_connection(conn)
        
        return jsonify({'success': True, 'count': len(data)})
    except Exception as e:
        conn.rollback()
        release_db_connection(conn)
        return jsonify({'success': False, 'error': str(e)}), 500

# API para obtener unidades reservadas
@app.route('/api/unidades_reservadas', methods=['GET'])
@login_required
def get_unidades_reservadas():
    # Verificar que tenga permiso de planeamiento O ventas
    if not (current_user.has_permission('planeamiento') or current_user.has_permission('ventas')):
        return jsonify({'error': 'No tienes permisos para acceder a esta información'}), 403
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT numero_fabrica, vendedor, fecha_agregado FROM unidades_reservadas ORDER BY fecha_agregado DESC')
    rows = cursor.fetchall()
    release_db_connection(conn)
    
    reservadas = []
    for row in rows:
        reservadas.append({
            'numero_fabrica': row['numero_fabrica'],
            'vendedor': row['vendedor'],
            'fecha_agregado': row['fecha_agregado']
        })
    return jsonify(reservadas)

# API para agregar unidad reservada
@app.route('/api/unidades_reservadas', methods=['POST'])
@login_required
def add_unidad_reservada():
    # Verificar que tenga permiso de planeamiento O ventas
    if not (current_user.has_permission('planeamiento') or current_user.has_permission('ventas')):
        return jsonify({'error': 'No tienes permisos para acceder a esta información'}), 403
    
    data = request.json
    numero_fabrica = data.get('numero_fabrica', '').strip()
    vendedor = data.get('vendedor', '').strip()
    
    if not numero_fabrica:
        return jsonify({'success': False, 'error': 'Número de fábrica vacío'}), 400
    
    if not vendedor:
        return jsonify({'success': False, 'error': 'Nombre del vendedor vacío'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT INTO unidades_reservadas (numero_fabrica, vendedor) VALUES (%s, %s)', (numero_fabrica, vendedor))
        conn.commit()
        release_db_connection(conn)
        return jsonify({'success': True})
    except PgIntegrityError:
        conn.rollback()
        release_db_connection(conn)
        return jsonify({'success': False, 'error': 'Número de fábrica ya existe'}), 400
    except Exception as e:
        conn.rollback()
        release_db_connection(conn)
        return jsonify({'success': False, 'error': str(e)}), 500

# API para eliminar unidad reservada
@app.route('/api/unidades_reservadas/<numero_fabrica>', methods=['DELETE'])
@login_required
def delete_unidad_reservada(numero_fabrica):
    # Verificar que tenga permiso de planeamiento O ventas
    if not (current_user.has_permission('planeamiento') or current_user.has_permission('ventas')):
        return jsonify({'error': 'No tienes permisos para acceder a esta información'}), 403
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM unidades_reservadas WHERE numero_fabrica = %s', (numero_fabrica,))
        conn.commit()
        release_db_connection(conn)
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        release_db_connection(conn)
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== API MÓDULO 6: RECAUDACIÓN ====================

@app.route('/api/recaudacion', methods=['GET'])
@login_required
@module_permission_required('planeamiento')
def get_recaudacion():
    """Obtener datos de recaudación desde disponibles (solo YAC - Ventas Convencionales)
    Excluye unidades con ubicación 'Preventa'"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Obtener unidades disponibles que son YAC (Ventas Convencionales)
    # Estas son las unidades que vienen del módulo 3 (Seguimiento) con cliente vacío
    # Excluimos las que tienen ubicación "Preventa"
    cursor.execute('''
        SELECT 
            numero_fabrica,
            modelo_version,
            ubicacion,
            precio_disponible
        FROM disponibles
        WHERE numero_fabrica LIKE 'YAC%'
        AND (ubicacion IS NULL OR UPPER(TRIM(ubicacion)) != 'PREVENTA')
    ''')
    
    unidades = cursor.fetchall()
    release_db_connection(conn)
    
    # Separar por Stock y No Stock según la ubicación
    en_stock = []
    no_stock = []
    
    for unidad in unidades:
        ubicacion = (unidad['ubicacion'] or '').upper().strip()
        precio = unidad['precio_disponible'] or 0
        
        data_item = {
            'numero_fabrica': unidad['numero_fabrica'],
            'modelo_version': unidad['modelo_version'],
            'ubicacion': unidad['ubicacion'],
            'precio': precio
        }
        
        # Verificar si está en stock (contiene la palabra "STOCK")
        if 'STOCK' in ubicacion:
            en_stock.append(data_item)
        else:
            no_stock.append(data_item)
    
    # Calcular totales
    total_en_stock = sum(item['precio'] for item in en_stock)
    total_no_stock = sum(item['precio'] for item in no_stock)
    total_general = total_en_stock + total_no_stock
    
    return jsonify({
        'success': True,
        'en_stock': {
            'unidades': en_stock,
            'cantidad': len(en_stock),
            'total': total_en_stock
        },
        'no_stock': {
            'unidades': no_stock,
            'cantidad': len(no_stock),
            'total': total_no_stock
        },
        'total_general': total_general,
        'cantidad_total': len(en_stock) + len(no_stock)
    })


# ==================== API BACKUP/RESTORE ====================

@app.route('/api/backup/download', methods=['GET'])
@login_required
def download_backup():
    """Descargar backup completo de la base de datos"""
    import io
    import tempfile
    import shutil
    
    try:
        # Crear archivo temporal
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        shutil.copy2('database.db', temp_db.name)
        temp_db.close()
        
        return send_file(
            temp_db.name,
            as_attachment=True,
            download_name=f'database_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db',
            mimetype='application/x-sqlite3'
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/backup/upload', methods=['POST'])
@login_required
@module_permission_required('planeamiento')
def upload_backup():
    """Restaurar base de datos desde backup"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No se encontró archivo'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No se seleccionó archivo'}), 400
        
        # Guardar backup actual por seguridad
        import shutil
        shutil.copy2('database.db', 'database_backup_before_restore.db')
        
        # Reemplazar con el nuevo archivo
        file.save('database.db')
        
        return jsonify({'success': True, 'message': 'Base de datos restaurada correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== API OBSERVACIONES (MÓDULO 5) ====================

@app.route('/api/observaciones/config_dias', methods=['GET'])
@login_required
@module_permission_required('planeamiento')
def get_config_dias():
    """Obtener configuración de días estándar y desvío por zona"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT zona, dias_estandar, dias_desvio FROM config_dias_zonas ORDER BY zona')
        rows = cursor.fetchall()
        release_db_connection(conn)
        
        # Convertir a lista para el frontend
        config = [dict(row) for row in rows]
        
        return jsonify(config)
    except Exception as e:
        if conn:
            release_db_connection(conn)
        return jsonify({'error': str(e)}), 500

@app.route('/api/observaciones/config_dias', methods=['POST'])
@login_required
@module_permission_required('planeamiento')
def save_config_dias():
    """Guardar configuración de días"""
    conn = None
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        zonas = data.get('zonas', [])
        
        if not zonas:
            return jsonify({'success': False, 'error': 'No se recibieron datos de zonas'}), 400
        
        for zona_data in zonas:
            cursor.execute('''
                INSERT INTO config_dias_zonas (zona, dias_estandar, dias_desvio, fecha_actualizacion)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (zona) 
                DO UPDATE SET 
                    dias_estandar = EXCLUDED.dias_estandar,
                    dias_desvio = EXCLUDED.dias_desvio,
                    fecha_actualizacion = CURRENT_TIMESTAMP
            ''', (zona_data['zona'], zona_data['dias_estandar'], zona_data['dias_desvio']))
        
        conn.commit()
        release_db_connection(conn)
        return jsonify({'success': True, 'message': f'{len(zonas)} zonas guardadas'})
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except:
                pass
            release_db_connection(conn)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/observaciones/matriz_codigos', methods=['GET'])
@login_required
@module_permission_required('planeamiento')
def get_matriz_codigos():
    """Obtener matriz de códigos de observación"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT clase, zona, codigos, es_zona_arribo FROM matriz_codigos_obs ORDER BY clase, zona')
        rows = cursor.fetchall()
        release_db_connection(conn)
        
        # Convertir a lista para el frontend
        matriz = [dict(row) for row in rows]
        
        return jsonify(matriz)
    except Exception as e:
        if conn:
            release_db_connection(conn)
        return jsonify({'error': str(e)}), 500

@app.route('/api/observaciones/matriz_codigos', methods=['POST'])
@login_required
@module_permission_required('planeamiento')
def save_matriz_codigos():
    """Guardar matriz de códigos"""
    conn = None
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        matriz = data.get('matriz', [])
        
        if not matriz:
            return jsonify({'success': False, 'error': 'No se recibieron datos de matriz'}), 400
        
        print(f"\n>> Guardando matriz de codigos: {len(matriz)} registros")
        
        # IMPORTANTE: Eliminar todos los registros existentes primero
        # para evitar registros huerfanos de configuraciones anteriores
        cursor.execute('DELETE FROM matriz_codigos_obs')
        print(f"   Registros anteriores eliminados")
        
        # Insertar nuevos registros
        for idx, registro in enumerate(matriz):
            try:
                # Extraer y validar valores
                clase = registro.get('clase')
                zona_raw = registro.get('zona')
                codigos = registro.get('codigos')
                es_zona_arribo = registro.get('es_zona_arribo', False)
                
                # Validaciones estrictas
                if not clase or not isinstance(clase, str):
                    raise ValueError(f"Clase inválida: {clase}")
                
                if not isinstance(zona_raw, int):
                    raise ValueError(f"Zona debe ser un número, recibido: {type(zona_raw).__name__} = {zona_raw}")
                
                zona = zona_raw
                if zona < 1 or zona > 4:
                    raise ValueError(f"Zona fuera de rango (1-4): {zona}")
                
                if codigos is None:
                    codigos = ''
                codigos = str(codigos).strip()
                
                # Convertir es_zona_arribo a booleano
                if isinstance(es_zona_arribo, bool):
                    pass  # Ya es booleano
                elif isinstance(es_zona_arribo, str):
                    es_zona_arribo = es_zona_arribo.lower() in ['true', '1', 'yes']
                elif isinstance(es_zona_arribo, (int, float)):
                    es_zona_arribo = bool(es_zona_arribo)
                else:
                    es_zona_arribo = False
                
                print(f"  [{idx}] {clase} Zona {zona}: '{codigos}' (arribo={es_zona_arribo})")
                
                cursor.execute('''
                    INSERT INTO matriz_codigos_obs (clase, zona, codigos, es_zona_arribo, fecha_actualizacion)
                    VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                ''', (clase, zona, codigos, es_zona_arribo))
                
            except ValueError as val_err:
                error_msg = f"Error de validacion en registro {idx}: {val_err}"
                print(f"  ERROR: {error_msg}")
                print(f"     Registro completo: {registro}")
                conn.rollback()
                release_db_connection(conn)
                return jsonify({'success': False, 'error': error_msg}), 400
            except Exception as row_error:
                error_msg = f"Error en registro {idx}: {str(row_error)}"
                print(f"  ERROR: {error_msg}")
                print(f"     Registro completo: {registro}")
                conn.rollback()
                release_db_connection(conn)
                return jsonify({'success': False, 'error': error_msg}), 500
        
        conn.commit()
        release_db_connection(conn)
        print(f">> OK - Matriz guardada exitosamente: {len(matriz)} registros")
        return jsonify({'success': True, 'message': f'{len(matriz)} registros guardados'})
        
    except Exception as e:
        error_msg = f"Error general guardando matriz: {str(e)}"
        print(f"ERROR: {error_msg}")
        if conn:
            try:
                conn.rollback()
            except:
                pass
            release_db_connection(conn)
        return jsonify({'success': False, 'error': error_msg}), 500

@app.route('/api/observaciones/registrar_cambio', methods=['POST'])
@login_required
@module_permission_required('planeamiento')
def registrar_cambio_observacion():
    """Registrar cambio de código de observación"""
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        operacion = data.get('operacion')
        codigo_nuevo = data.get('codigo_nuevo')
        zona_nueva = data.get('zona_nueva')
        ejecutivo = data.get('ejecutivo')
        
        # Obtener último cambio
        cursor.execute('''
            SELECT codigo_nuevo as codigo, zona_nueva as zona
            FROM auditoria_observaciones
            WHERE operacion = %s
            ORDER BY fecha_cambio DESC
            LIMIT 1
        ''', (operacion,))
        
        ultimo = cursor.fetchone()
        codigo_anterior = ultimo['codigo'] if ultimo else None
        zona_anterior = ultimo['zona'] if ultimo else None
        
        # Detectar retroceso
        es_retroceso = False
        if zona_anterior and zona_nueva and zona_nueva < zona_anterior:
            es_retroceso = True
        
        # Insertar auditoría
        cursor.execute('''
            INSERT INTO auditoria_observaciones 
            (operacion, codigo_anterior, codigo_nuevo, zona_anterior, zona_nueva, ejecutivo, es_retroceso)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (operacion, codigo_anterior, codigo_nuevo, zona_anterior, zona_nueva, ejecutivo, es_retroceso))
        
        # Actualizar estadísticas
        cursor.execute('''
            INSERT INTO stats_operaciones (operacion, cantidad_cambios, cantidad_retrocesos, marcado_sospechoso)
            VALUES (%s, 1, %s, %s)
            ON CONFLICT (operacion)
            DO UPDATE SET
                cantidad_cambios = stats_operaciones.cantidad_cambios + 1,
                cantidad_retrocesos = stats_operaciones.cantidad_retrocesos + CASE WHEN %s THEN 1 ELSE 0 END,
                marcado_sospechoso = CASE WHEN stats_operaciones.cantidad_retrocesos + CASE WHEN %s THEN 1 ELSE 0 END > 1 THEN TRUE ELSE FALSE END,
                fecha_actualizacion = CURRENT_TIMESTAMP
        ''', (operacion, 1 if es_retroceso else 0, es_retroceso, es_retroceso, es_retroceso))
        
        conn.commit()
        release_db_connection(conn)
        return jsonify({'success': True, 'es_retroceso': es_retroceso})
    except Exception as e:
        conn.rollback()
        release_db_connection(conn)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/observaciones/stats/<operacion>', methods=['GET'])
@login_required
@module_permission_required('planeamiento')
def get_stats_operacion(operacion):
    """Obtener estadísticas de una operación"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT cantidad_cambios, cantidad_retrocesos, marcado_sospechoso
            FROM stats_operaciones
            WHERE operacion = %s
        ''', (operacion,))
        
        row = cursor.fetchone()
        release_db_connection(conn)
        
        if row:
            return jsonify({
                'success': True,
                'stats': {
                    'cantidad_cambios': row['cantidad_cambios'],
                    'cantidad_retrocesos': row['cantidad_retrocesos'],
                    'marcado_sospechoso': row['marcado_sospechoso']
                }
            })
        else:
            return jsonify({
                'success': True,
                'stats': {
                    'cantidad_cambios': 0,
                    'cantidad_retrocesos': 0,
                    'marcado_sospechoso': False
                }
            })
    except Exception as e:
        conn.rollback()
        release_db_connection(conn)
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== API BUSINESS INTELLIGENCE ====================

@app.route('/api/bi/upload_databases', methods=['POST'])
@login_required
def upload_bi_databases():
    """Cargar y procesar archivos de bases de datos para BI"""
    try:
        files = request.files
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Solo verificar archivos de patentamientos (ignorar entregas)
        required_files = [
            'argentina-marca', 'argentina-modelo', 
            'mendoza-marca', 'mendoza-modelo'
        ]
        
        for file_key in required_files:
            if file_key not in files:
                return jsonify({'success': False, 'error': f'Falta el archivo: {file_key}'}), 400
            # Verificar que el archivo tenga nombre válido
            file = files[file_key]
            if not file.filename or file.filename == '':
                return jsonify({'success': False, 'error': f'Archivo inválido: {file_key}'}), 400
        
        # Procesar archivos de patentamientos
        import pandas as pd
        from dateutil import parser as date_parser
        
        # Diccionario para convertir nombres de meses en español
        meses_es = {
            'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
            'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
            'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12,
            'ene': 1, 'feb': 2, 'mar': 3, 'abr': 4,
            'may': 5, 'jun': 6, 'jul': 7, 'ago': 8,
            'sep': 9, 'oct': 10, 'nov': 11, 'dic': 12
        }
        
        # Limpiar tablas anteriores
        cursor.execute('DELETE FROM bi_patentamientos_argentina_marca')
        cursor.execute('DELETE FROM bi_patentamientos_argentina_modelo')
        cursor.execute('DELETE FROM bi_patentamientos_mendoza_marca')
        cursor.execute('DELETE FROM bi_patentamientos_mendoza_modelo')
        
        print("🔄 Comenzando procesamiento de archivos...")
        
        # Procesar cada archivo
        for file_key in ['argentina-marca', 'argentina-modelo', 'mendoza-marca', 'mendoza-modelo']:
            file = files[file_key]
            print(f"\n📂 Procesando archivo: {file_key} ({file.filename})")
            
            # Leer Excel sin forzar tipos
            df = pd.read_excel(file, dtype=str)
            print(f"   ✓ Archivo leído: {len(df)} filas, {len(df.columns)} columnas")
            print(f"   Columnas detectadas: {list(df.columns)}")
            
            # La primera columna es el nombre (marca o modelo)
            nombre_columna = df.columns[0]
            fechas_columnas = df.columns[1:]
            
            print(f"   Columna de nombres: '{nombre_columna}'")
            print(f"   Primeras 3 fechas: {list(fechas_columnas[:3])}")
            
            # Determinar tabla destino
            if file_key == 'argentina-marca':
                tabla = 'bi_patentamientos_argentina_marca'
            elif file_key == 'argentina-modelo':
                tabla = 'bi_patentamientos_argentina_modelo'
            elif file_key == 'mendoza-marca':
                tabla = 'bi_patentamientos_mendoza_marca'
            else:  # mendoza-modelo
                tabla = 'bi_patentamientos_mendoza_modelo'
            
            registros_insertados = 0
            errores = 0
            
            # Insertar datos
            for idx, row in df.iterrows():
                nombre = str(row[nombre_columna]).strip()
                
                # Saltar filas vacías
                if pd.isna(nombre) or nombre == '' or nombre == 'nan':
                    continue
                
                # Insertar cada mes
                for fecha_col in fechas_columnas:
                    valor = row[fecha_col]
                    
                    # Convertir valor a número
                    try:
                        if pd.isna(valor) or valor == '' or valor == 'nan':
                            cantidad = 0
                        else:
                            cantidad = int(float(str(valor).replace(',', '.')))
                    except:
                        cantidad = 0
                    
                    # Parsear fecha (puede venir como "enero-15", "01/15", o timestamp de pandas)
                    try:
                        fecha_str = str(fecha_col).strip().lower()
                        
                        # Caso 1: Formato "enero-15" o "ene-15"
                        if '-' in fecha_str:
                            partes = fecha_str.split('-')
                            mes_nombre = partes[0].strip()
                            anio = partes[1].strip()
                            
                            # Buscar el mes en el diccionario
                            mes = meses_es.get(mes_nombre, None)
                            if mes is None:
                                print(f"   ⚠️ Mes no reconocido: '{mes_nombre}'")
                                continue
                            
                            # Convertir año a 4 dígitos
                            if len(anio) == 2:
                                anio = '20' + anio
                            
                            fecha = f"{anio}-{str(mes).zfill(2)}-01"
                        
                        # Caso 2: Formato "01/15" o "1/15"
                        elif '/' in fecha_str:
                            partes = fecha_str.split('/')
                            mes = int(partes[0])
                            anio = partes[1].strip()
                            
                            if len(anio) == 2:
                                anio = '20' + anio
                            
                            fecha = f"{anio}-{str(mes).zfill(2)}-01"
                        
                        # Caso 3: Timestamp de pandas
                        elif isinstance(fecha_col, pd.Timestamp):
                            fecha = fecha_col.strftime('%Y-%m-%d')
                        
                        # Caso 4: Intentar parsear con dateutil
                        else:
                            try:
                                fecha_obj = date_parser.parse(fecha_str, dayfirst=True)
                                fecha = fecha_obj.strftime('%Y-%m-01')
                            except:
                                print(f"   ⚠️ Fecha no reconocida: '{fecha_str}'")
                                continue
                        
                        # Insertar en base de datos
                        cursor.execute(f'''
                            INSERT INTO {tabla} (nombre, fecha, cantidad)
                            VALUES (%s, %s, %s)
                        ''', (nombre, fecha, cantidad))
                        
                        registros_insertados += 1
                        
                    except Exception as e:
                        errores += 1
                        if errores < 5:  # Mostrar solo los primeros 5 errores
                            print(f"   ⚠️ Error procesando fecha '{fecha_col}': {e}")
            
            print(f"   ✅ Insertados: {registros_insertados} registros | Errores: {errores}")
        
        conn.commit()
        
        # Obtener contadores de filas
        row_counts = {}
        cursor.execute('SELECT COUNT(*) as total FROM bi_patentamientos_argentina_marca')
        row_counts['argentina-marca'] = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as total FROM bi_patentamientos_argentina_modelo')
        row_counts['argentina-modelo'] = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as total FROM bi_patentamientos_mendoza_marca')
        row_counts['mendoza-marca'] = cursor.fetchone()['total']
        
        cursor.execute('SELECT COUNT(*) as total FROM bi_patentamientos_mendoza_modelo')
        row_counts['mendoza-modelo'] = cursor.fetchone()['total']
        
        release_db_connection(conn)
        
        # INVALIDAR CACHÉ cuando se cargan nuevos datos
        patentamientos_cache['data'] = None
        patentamientos_cache['timestamp'] = 0
        print("🗑️ Caché de patentamientos invalidado")
        
        return jsonify({
            'success': True, 
            'message': 'Archivos procesados correctamente',
            'rowCounts': row_counts
        })
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            release_db_connection(conn)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/bi/patentamientos', methods=['GET'])
@login_required
def get_bi_patentamientos():
    """Obtener datos de patentamientos DIRECTAMENTE desde CSV - CON CACHÉ"""
    try:
        # Verificar si el caché es válido
        current_time = time()
        force_refresh = request.args.get('refresh', 'false').lower() == 'true'
        
        if (not force_refresh and 
            patentamientos_cache['data'] is not None and 
            (current_time - patentamientos_cache['timestamp']) < patentamientos_cache['ttl']):
            print("✅ Sirviendo datos desde CACHÉ")
            return jsonify({'success': True, 'data': patentamientos_cache['data'], 'from_cache': True})
        
        print("🔄 Cargando datos desde CSV...")
        
        # Leer datos desde CSV
        result = {
            'argentina_marca': get_patentamientos_from_csv('Mercado Argentino MARCA.csv', 'marca'),
            'argentina_modelo': get_patentamientos_from_csv('Mercado Argentino MODELO.csv', 'modelo'),
            'mendoza_marca': get_patentamientos_from_csv('Mercado Mendoza MARCA.csv', 'marca'),
            'mendoza_modelo': get_patentamientos_from_csv('Mercado Mendoza MODELO.csv', 'modelo')
        }
        
        # Guardar en caché
        patentamientos_cache['data'] = result
        patentamientos_cache['timestamp'] = current_time
        print(f"💾 Datos guardados en caché (válido por {patentamientos_cache['ttl']}s)")
        
        return jsonify({'success': True, 'data': result, 'from_cache': False})
    except FileNotFoundError as e:
        return jsonify({'success': False, 'error': f'Archivos CSV no encontrados: {str(e)}'}), 404
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


def get_patentamientos_from_csv(filename, tipo):
    """Leer y procesar datos de patentamientos desde CSV"""
    csv_path = os.path.join(os.path.dirname(__file__), 'Patentamientos', filename)
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Archivo no encontrado: {csv_path}")
    
    # Leer CSV con diferentes encodings
    df = None
    for encoding in ['latin-1', 'cp1252', 'iso-8859-1', 'utf-8']:
        try:
            df = pd.read_csv(csv_path, delimiter=';', encoding=encoding)
            break
        except:
            continue
    
    if df is None:
        raise Exception(f"No se pudo leer el archivo {filename}")
    
    # Primera columna es el nombre (marca o modelo)
    nombres_col = df.columns[0]
    
    # Resto de columnas son fechas (ene-15, feb-15, etc.)
    fecha_cols = df.columns[1:]
    
    # Convertir nombres de columnas de fecha a formato MM/YY
    meses_map = {
        'ene': '01', 'feb': '02', 'mar': '03', 'abr': '04',
        'may': '05', 'jun': '06', 'jul': '07', 'ago': '08',
        'sep': '09', 'oct': '10', 'nov': '11', 'dic': '12'
    }
    
    fechas_formateadas = []
    for col in fecha_cols:
        col_lower = str(col).lower().strip()
        if '-' in col_lower:
            mes_str, anio_str = col_lower.split('-')
            mes = meses_map.get(mes_str.strip())
            anio = anio_str.strip()
            if mes and len(anio) == 2:
                fechas_formateadas.append(f"{mes}/{anio}")
            else:
                fechas_formateadas.append(col)
        else:
            fechas_formateadas.append(col)
    
    if tipo == 'marca':
        return get_datos_por_marca(df, nombres_col, fecha_cols, fechas_formateadas)
    else:
        return get_datos_por_modelo(df, nombres_col, fecha_cols, fechas_formateadas)


def get_datos_por_marca(df, nombres_col, fecha_cols, fechas_formateadas):
    """Procesar datos agrupados por marca"""
    marcas = ['TOYOTA', 'FORD', 'FIAT', 'VOLKSWAGEN', 'CHEVROLET', 'PEUGEOT']
    result = {'labels': fechas_formateadas}
    
    # Inicializar series para cada marca
    for marca in marcas:
        result[marca.lower()] = [0] * len(fecha_cols)
    result['otros'] = [0] * len(fecha_cols)
    
    # Procesar cada fila
    for idx, row in df.iterrows():
        nombre = str(row[nombres_col]).upper().strip()
        
        for i, fecha_col in enumerate(fecha_cols):
            valor = row[fecha_col]
            try:
                cantidad = int(float(valor)) if pd.notna(valor) else 0
            except:
                cantidad = 0
            
            # Clasificar por marca
            marca_encontrada = False
            for marca in marcas:
                if marca in nombre:
                    result[marca.lower()][i] += cantidad
                    marca_encontrada = True
                    break
            
            if not marca_encontrada:
                result['otros'][i] += cantidad
    
    return result


def get_datos_por_modelo(df, nombres_col, fecha_cols, fechas_formateadas):
    """Procesar datos por modelo con Top 5"""
    # Obtener datos de la última columna para Top 5
    ultima_col = fecha_cols[-1]
    
    # Crear lista de (nombre, valor_ultimo_mes) y ordenar
    modelos_ultimo_mes = []
    for idx, row in df.iterrows():
        nombre = str(row[nombres_col]).strip()
        valor = row[ultima_col]
        try:
            cantidad = int(float(valor)) if pd.notna(valor) else 0
        except:
            cantidad = 0
        
        if cantidad > 0:
            modelos_ultimo_mes.append({'nombre': nombre, 'cantidad': cantidad})
    
    # Ordenar y obtener Top 5
    modelos_ultimo_mes.sort(key=lambda x: x['cantidad'], reverse=True)
    top5_ultimo_mes = modelos_ultimo_mes[:5]
    
    # Procesar todos los modelos con sus valores históricos
    modelos = []
    for idx, row in df.iterrows():
        nombre = str(row[nombres_col]).strip()
        valores = []
        
        for fecha_col in fecha_cols:
            valor = row[fecha_col]
            try:
                cantidad = int(float(valor)) if pd.notna(valor) else 0
            except:
                cantidad = 0
            valores.append(cantidad)
        
        modelos.append({
            'nombre': nombre,
            'valores': valores
        })
    
    return {
        'labels': fechas_formateadas,
        'modelos': modelos,
        'top5_ultimo_mes': top5_ultimo_mes
    }


def get_patentamientos_marca(cursor, tabla):
    """Obtener datos agrupados por marca - OPTIMIZADO con una consulta"""
    # Obtener todas las fechas distintas ordenadas
    cursor.execute(f'SELECT DISTINCT fecha FROM {tabla} ORDER BY fecha')
    fechas = [row['fecha'].strftime('%m/%y') for row in cursor.fetchall()]
    
    marcas = ['TOYOTA', 'FORD', 'FIAT', 'VOLKSWAGEN', 'CHEVROLET', 'PEUGEOT']
    result = {'labels': fechas}
    
    # Inicializar diccionarios para cada marca
    for marca in marcas:
        result[marca.lower()] = [0] * len(fechas)
    result['otros'] = [0] * len(fechas)
    
    # Obtener todos los datos en una sola consulta
    cursor.execute(f'SELECT fecha, nombre, cantidad FROM {tabla} ORDER BY fecha')
    
    fecha_to_index = {fecha: idx for idx, fecha in enumerate(fechas)}
    
    for row in cursor.fetchall():
        fecha_str = row['fecha'].strftime('%m/%y')
        nombre_upper = row['nombre'].upper()
        cantidad = row['cantidad']
        idx = fecha_to_index.get(fecha_str)
        
        if idx is None:
            continue
        
        # Clasificar por marca
        marca_encontrada = False
        for marca in marcas:
            if marca in nombre_upper:
                result[marca.lower()][idx] += cantidad
                marca_encontrada = True
                break
        
        if not marca_encontrada:
            result['otros'][idx] += cantidad
    
    return result


def get_patentamientos_modelo(cursor, tabla):
    """Obtener datos por modelo - OPTIMIZADO con una sola consulta"""
    # Obtener fechas
    cursor.execute(f'SELECT DISTINCT fecha FROM {tabla} ORDER BY fecha')
    fechas_rows = cursor.fetchall()
    fechas = [row['fecha'].strftime('%m/%y') for row in fechas_rows]
    fechas_dict = {row['fecha'].strftime('%m/%y'): row['fecha'] for row in fechas_rows}
    
    # Obtener la última fecha disponible
    cursor.execute(f'SELECT MAX(fecha) as ultima_fecha FROM {tabla}')
    ultima_fecha = cursor.fetchone()['ultima_fecha']
    
    # Obtener Top 5 del último mes
    cursor.execute(f'''
        SELECT nombre, cantidad
        FROM {tabla}
        WHERE fecha = %s
        ORDER BY cantidad DESC
        LIMIT 5
    ''', (ultima_fecha,))
    
    top5_ultimo_mes = [{'nombre': row['nombre'], 'cantidad': row['cantidad']} for row in cursor.fetchall()]
    
    # OPTIMIZACIÓN: Obtener TODOS los datos en una sola consulta
    cursor.execute(f'''
        SELECT nombre, fecha, cantidad
        FROM {tabla}
        ORDER BY nombre, fecha
    ''')
    
    # Construir estructura de datos eficientemente
    modelos_dict = {}
    for row in cursor.fetchall():
        nombre = row['nombre']
        fecha_str = row['fecha'].strftime('%m/%y')
        cantidad = row['cantidad']
        
        if nombre not in modelos_dict:
            modelos_dict[nombre] = {fecha_str: cantidad}
        else:
            modelos_dict[nombre][fecha_str] = cantidad
    
    # Convertir a formato esperado por el frontend
    modelos = []
    for nombre, valores_dict in modelos_dict.items():
        valores = [valores_dict.get(fecha, 0) for fecha in fechas]
        modelos.append({
            'nombre': nombre,
            'valores': valores
        })
    
    return {
        'labels': fechas,
        'modelos': modelos,
        'top5_ultimo_mes': top5_ultimo_mes
    }


@app.route('/api/bi/save_manual_data', methods=['POST'])
@login_required
def save_manual_data():
    """Guardar solo MES ACTUAL - Actualización rápida"""
    conn = None
    try:
        data = request.get_json()
        data_type = data.get('dataType')
        headers = data.get('headers')
        rows = data.get('rows')
        
        if not all([data_type, headers, rows]):
            return jsonify({'success': False, 'error': 'Datos incompletos'}), 400
        
        # Mapeo de tablas
        tabla_map = {
            'argentina-marca': 'bi_patentamientos_argentina_marca',
            'argentina-modelo': 'bi_patentamientos_argentina_modelo',
            'mendoza-marca': 'bi_patentamientos_mendoza_marca',
            'mendoza-modelo': 'bi_patentamientos_mendoza_modelo'
        }
        
        if data_type not in tabla_map:
            return jsonify({'success': False, 'error': 'Tipo de datos inválido'}), 400
        
        tabla = tabla_map[data_type]
        
        # Diccionario de meses
        meses_es = {
            'ene': 1, 'feb': 2, 'mar': 3, 'abr': 4,
            'may': 5, 'jun': 6, 'jul': 7, 'ago': 8,
            'sep': 9, 'oct': 10, 'nov': 11, 'dic': 12
        }
        
        print(f"\n📝 Actualizando MES ACTUAL para {data_type}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # IDENTIFICAR EL ÚLTIMO MES (columna más reciente)
        ultima_columna_idx = len(headers) - 1
        fecha_col = str(headers[ultima_columna_idx]).strip().lower()
        
        print(f"   📅 Última columna detectada: {fecha_col}")
        
        # Parsear la fecha del último mes
        if '-' in fecha_col:
            partes = fecha_col.split('-')
            mes_nombre = partes[0].strip()
            anio = partes[1].strip()
            
            mes = meses_es.get(mes_nombre)
            if not mes:
                return jsonify({'success': False, 'error': f'Mes no reconocido: {mes_nombre}'}), 400
            
            if len(anio) == 2:
                anio = '20' + anio if int(anio) <= 50 else '19' + anio
            
            fecha_actualizar = f"{anio}-{str(mes).zfill(2)}-01"
        else:
            return jsonify({'success': False, 'error': 'Formato de fecha no reconocido'}), 400
        
        print(f"   🎯 Actualizando datos para: {fecha_actualizar}")
        
        # Preparar registros SOLO del último mes
        registros = []
        
        for row_data in rows:
            nombre = str(row_data[0]).strip()
            if not nombre or nombre.lower() in ['', 'nan', 'none']:
                continue
            
            # Obtener valor del último mes
            if ultima_columna_idx < len(row_data):
                valor_str = row_data[ultima_columna_idx]
                
                try:
                    if not valor_str or str(valor_str).lower() in ['', 'nan', 'none']:
                        cantidad = 0
                    else:
                        cantidad = int(float(str(valor_str).replace(',', '').replace('.', '')))
                except:
                    cantidad = 0
                
                registros.append((nombre, fecha_actualizar, cantidad))
        
        # Insertar/Actualizar en batch
        print(f"   🔄 Actualizando {len(registros)} marcas/modelos...")
        
        values_placeholders = ','.join(['(%s, %s, %s)'] * len(registros))
        flat_values = [item for tupla in registros for item in tupla]
        
        cursor.execute(f'''
            INSERT INTO {tabla} (nombre, fecha, cantidad)
            VALUES {values_placeholders}
            ON CONFLICT (nombre, fecha) 
            DO UPDATE SET cantidad = EXCLUDED.cantidad, fecha_carga = CURRENT_TIMESTAMP
        ''', flat_values)
        
        conn.commit()
        
        cursor.execute(f'SELECT COUNT(*) as total FROM {tabla}')
        total = cursor.fetchone()['total']
        
        release_db_connection(conn)
        
        # INVALIDAR CACHÉ cuando se actualizan datos manualmente
        patentamientos_cache['data'] = None
        patentamientos_cache['timestamp'] = 0
        print("🗑️ Caché de patentamientos invalidado")
        
        print(f"   ✅ Actualizado: {len(registros)} registros para {fecha_actualizar}")
        
        return jsonify({
            'success': True,
            'message': f'Mes actual actualizado: {fecha_actualizar}',
            'recordsSaved': len(registros),
            'totalRecords': total,
            'updatedMonth': fecha_actualizar
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
        if conn:
            conn.rollback()
            release_db_connection(conn)
        
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/bi/get_saved_data/<data_type>', methods=['GET'])
@login_required
def get_saved_data(data_type):
    """Obtener datos guardados de una tabla específica"""
    try:
        # Determinar tabla origen
        tabla_map = {
            'argentina-marca': 'bi_patentamientos_argentina_marca',
            'argentina-modelo': 'bi_patentamientos_argentina_modelo',
            'mendoza-marca': 'bi_patentamientos_mendoza_marca',
            'mendoza-modelo': 'bi_patentamientos_mendoza_modelo'
        }
        
        if data_type not in tabla_map:
            return jsonify({'success': False, 'error': 'Tipo de datos inválido'}), 400
        
        tabla = tabla_map[data_type]
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar si hay datos
        cursor.execute(f'SELECT COUNT(*) as total FROM {tabla}')
        total = cursor.fetchone()['total']
        
        if total == 0:
            release_db_connection(conn)
            return jsonify({'success': True, 'hasData': False})
        
        # Obtener todas las fechas únicas ordenadas
        cursor.execute(f'SELECT DISTINCT fecha FROM {tabla} ORDER BY fecha')
        fechas_raw = cursor.fetchall()
        
        # Formatear fechas como "ene-15", "feb-15", etc.
        meses_nombres = {
            1: 'ene', 2: 'feb', 3: 'mar', 4: 'abr', 5: 'may', 6: 'jun',
            7: 'jul', 8: 'ago', 9: 'sep', 10: 'oct', 11: 'nov', 12: 'dic'
        }
        
        fechas = []
        for row in fechas_raw:
            fecha_obj = row['fecha']
            mes_nombre = meses_nombres[fecha_obj.month]
            anio_corto = str(fecha_obj.year)[-2:]
            fechas.append(f"{mes_nombre}-{anio_corto}")
        
        # Obtener todos los nombres únicos ordenados
        cursor.execute(f'SELECT DISTINCT nombre FROM {tabla} ORDER BY nombre')
        nombres_raw = cursor.fetchall()
        nombres = [row['nombre'] for row in nombres_raw]
        
        # Obtener TODOS los datos en una sola consulta (OPTIMIZACIÓN CRÍTICA)
        cursor.execute(f'SELECT nombre, fecha, cantidad FROM {tabla} ORDER BY nombre, fecha')
        todos_los_datos = cursor.fetchall()
        
        # Crear diccionario para acceso rápido: {(nombre, fecha): cantidad}
        datos_dict = {}
        for row in todos_los_datos:
            key = (row['nombre'], row['fecha'])
            datos_dict[key] = row['cantidad']
        
        # Construir matriz de datos usando el diccionario
        rows_data = []
        for nombre in nombres:
            row = [nombre]
            
            # Para cada fecha, obtener la cantidad del diccionario
            for fecha_obj_wrapper in fechas_raw:
                fecha_obj = fecha_obj_wrapper['fecha']
                cantidad = datos_dict.get((nombre, fecha_obj), 0)
                row.append(cantidad)
            
            rows_data.append(row)
        
        # Obtener fecha de última actualización
        cursor.execute(f'SELECT MAX(fecha_carga) as ultima_actualizacion FROM {tabla}')
        ultima_act = cursor.fetchone()['ultima_actualizacion']
        
        release_db_connection(conn)
        
        return jsonify({
            'success': True,
            'hasData': True,
            'headers': ['Marca/Modelo'] + fechas,
            'rows': rows_data,
            'totalRecords': total,
            'lastUpdate': ultima_act.strftime('%Y-%m-%d %H:%M:%S') if ultima_act else None
        })
        
    except Exception as e:
        print(f"❌ Error obteniendo datos guardados: {e}")
        if 'conn' in locals():
            release_db_connection(conn)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/bi/load_historical_data', methods=['POST'])
@login_required
def load_historical_data():
    """Invalidar caché y forzar recarga desde CSV"""
    patentamientos_cache['data'] = None
    patentamientos_cache['timestamp'] = 0
    return jsonify({'success': True, 'message': 'Caché invalidado. Los datos se recargarán en la próxima consulta.'})


@app.route('/api/bi/load_status', methods=['GET'])
@login_required
def get_load_status():
    """Verificar estado de los archivos CSV"""
    csv_dir = os.path.join(os.path.dirname(__file__), 'Patentamientos')
    archivos = [
        'Mercado Argentino MARCA.csv',
        'Mercado Argentino MODELO.csv',
        'Mercado Mendoza MARCA.csv',
        'Mercado Mendoza MODELO.csv'
    ]
    
    status = []
    for archivo in archivos:
        path = os.path.join(csv_dir, archivo)
        if os.path.exists(path):
            stat = os.stat(path)
            status.append({
                'archivo': archivo,
                'existe': True,
                'tamano': stat.st_size,
                'ultima_modificacion': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            })
        else:
            status.append({
                'archivo': archivo,
                'existe': False
            })
    
    return jsonify({
        'archivos': status,
        'cache_activo': patentamientos_cache['data'] is not None
    })


# ================================
# RETAIL Y PLAN DE NEGOCIO ROUTES
# ================================

def extract_family(modelo):
    """Extract vehicle family from model name"""
    modelo_upper = str(modelo).upper()
    
    # Priority order matters (check COROLLA CROSS before COROLLA)
    if 'COROLLA CROSS' in modelo_upper:
        return 'COROLLA CROSS'
    elif 'YARIS CROSS' in modelo_upper:
        return 'YARIS CROSS'
    elif 'COROLLA' in modelo_upper:
        return 'COROLLA'
    elif 'HILUX' in modelo_upper:
        return 'HILUX'
    elif 'SW4' in modelo_upper:
        return 'SW4'
    elif 'YARIS' in modelo_upper:
        return 'YARIS'
    elif 'RAV' in modelo_upper or 'RAV4' in modelo_upper:
        return 'RAV 4'
    elif 'HIACE' in modelo_upper:
        return 'HIACE'
    else:
        return 'OTROS'


@app.route('/bi/retail_plan')
@login_required
def retail_plan():
    """Página del módulo Retail y Plan de Negocio"""
    return render_template('bi_retail_plan.html')


@app.route('/api/retail/plan', methods=['GET'])
@login_required
def get_retail_plan():
    """Obtener objetivos del plan de negocio"""
    try:
        anio = request.args.get('anio', 2025, type=int)
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT familia, convencional_objetivo, especificas_objetivo, tpa_objetivo
            FROM retail_plan
            WHERE anio = %s
            ORDER BY familia
        """, (anio,))
        
        resultados = cur.fetchall()
        plan = {}
        for row in resultados:
            plan[row['familia']] = {
                'convencional': row['convencional_objetivo'],
                'especificas': row['especificas_objetivo'],
                'tpa': row['tpa_objetivo'],
                'total': row['convencional_objetivo'] + row['especificas_objetivo'] + row['tpa_objetivo']
            }
        
        cur.close()
        conn.close()
        
        return jsonify({'success': True, 'plan': plan})
    except Exception as e:
        print(f"Error obteniendo plan: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/retail/plan', methods=['POST'])
@login_required
def update_retail_plan():
    """Actualizar objetivos del plan de negocio"""
    try:
        data = request.get_json()
        anio = data.get('anio', 2025)
        familia = data['familia']
        convencional = data['convencional']
        especificas = data['especificas']
        tpa = data['tpa']
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO retail_plan 
            (anio, familia, convencional_objetivo, especificas_objetivo, tpa_objetivo, updated_at)
            VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (anio, familia) 
            DO UPDATE SET 
                convencional_objetivo = EXCLUDED.convencional_objetivo,
                especificas_objetivo = EXCLUDED.especificas_objetivo,
                tpa_objetivo = EXCLUDED.tpa_objetivo,
                updated_at = CURRENT_TIMESTAMP
        """, (anio, familia, convencional, especificas, tpa))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error actualizando plan: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/retail/sales_vs_plan', methods=['GET'])
@login_required
def sales_vs_plan():
    """Comparar ventas reales vs plan de negocio con desvío acumulado diario"""
    try:
        anio = request.args.get('anio', 2025, type=int)
        
        # Promedios mensuales de patentamiento histórico y días por mes
        datos_mensuales = {
            1: {'porcentaje': 11.54, 'dias': 31},   # Enero
            2: {'porcentaje': 7.29, 'dias': 28},    # Febrero (ajustar para bisiestos)
            3: {'porcentaje': 8.37, 'dias': 31},    # Marzo
            4: {'porcentaje': 7.76, 'dias': 30},    # Abril
            5: {'porcentaje': 8.37, 'dias': 31},    # Mayo
            6: {'porcentaje': 9.25, 'dias': 30},    # Junio
            7: {'porcentaje': 9.25, 'dias': 31},    # Julio
            8: {'porcentaje': 9.43, 'dias': 31},    # Agosto
            9: {'porcentaje': 8.65, 'dias': 30},    # Septiembre
            10: {'porcentaje': 8.80, 'dias': 31},   # Octubre
            11: {'porcentaje': 7.79, 'dias': 30},   # Noviembre
            12: {'porcentaje': 3.99, 'dias': 31}    # Diciembre
        }
        
        # Calcular porcentaje acumulado hasta hoy considerando días exactos
        from datetime import datetime
        hoy = datetime.now()
        mes_actual = hoy.month
        dia_actual = hoy.day
        
        # Acumular meses completos anteriores
        porcentaje_esperado_acumulado = sum(datos_mensuales[m]['porcentaje'] for m in range(1, mes_actual))
        
        # Calcular porcentaje diario del mes actual
        porcentaje_diario_mes_actual = datos_mensuales[mes_actual]['porcentaje'] / datos_mensuales[mes_actual]['dias']
        
        # Agregar los días transcurridos del mes actual
        porcentaje_esperado_acumulado += (porcentaje_diario_mes_actual * dia_actual)
        
        print(f"🗓️ Fecha: {dia_actual}/{mes_actual}/{anio} | Porcentaje esperado acumulado: {porcentaje_esperado_acumulado:.2f}%")
        
        # Leer CSV de retail
        csv_path = os.path.join(os.path.dirname(__file__), 'Retail y Plan de Negocio', 'Retail y Plan de Negocio.csv')
        
        # Try different encodings
        df = None
        for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
            try:
                df = pd.read_csv(csv_path, sep=';', encoding=encoding)
                break
            except:
                continue
        
        if df is None:
            return jsonify({'success': False, 'error': 'No se pudo leer el archivo CSV'}), 500
        
        # Extract family and sale type
        df['Familia'] = df['Modelo / Versión'].apply(extract_family)
        
        sale_type_map = {
            'YAC': 'Convencional',
            'TPA': 'Plan Ahorro',
            'F02': 'Vtas Especiales'
        }
        df['Tipo_Venta'] = df['Orden'].str[:3].map(sale_type_map)
        
        # Filter by year if Fecha column exists
        if 'Fecha' in df.columns:
            df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y', errors='coerce')
            df = df[df['Fecha'].dt.year == anio]
        
        # Group by family and sale type
        ventas_reales = df.groupby(['Familia', 'Tipo_Venta']).size().unstack(fill_value=0)
        
        # Get plan objectives
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT familia, convencional_objetivo, especificas_objetivo, tpa_objetivo
            FROM retail_plan
            WHERE anio = %s
            ORDER BY familia
        """, (anio,))
        
        plan_data = {}
        resultados_db = cur.fetchall()
        
        for row in resultados_db:
            familia = row['familia']
            plan_data[familia] = {
                'Convencional': row['convencional_objetivo'],
                'Vtas Especiales': row['especificas_objetivo'],
                'Plan Ahorro': row['tpa_objetivo']
            }
        
        cur.close()
        conn.close()
        
        # Build comparison data with accumulated deviation logic
        familias = list(set(list(ventas_reales.index) + list(plan_data.keys())))
        resultados = []
        
        for familia in familias:
            real_conv = ventas_reales.loc[familia, 'Convencional'] if familia in ventas_reales.index and 'Convencional' in ventas_reales.columns else 0
            real_espec = ventas_reales.loc[familia, 'Vtas Especiales'] if familia in ventas_reales.index and 'Vtas Especiales' in ventas_reales.columns else 0
            real_tpa = ventas_reales.loc[familia, 'Plan Ahorro'] if familia in ventas_reales.index and 'Plan Ahorro' in ventas_reales.columns else 0
            
            plan_conv = plan_data.get(familia, {}).get('Convencional', 0)
            plan_espec = plan_data.get(familia, {}).get('Vtas Especiales', 0)
            plan_tpa = plan_data.get(familia, {}).get('Plan Ahorro', 0)
            
            # Calcular objetivo acumulado esperado hasta ahora (enteros)
            objetivo_acum_conv = int(plan_conv * porcentaje_esperado_acumulado / 100)
            objetivo_acum_espec = int(plan_espec * porcentaje_esperado_acumulado / 100)
            objetivo_acum_tpa = int(plan_tpa * porcentaje_esperado_acumulado / 100)
            
            # Calcular desvío: (real - objetivo_acumulado) / objetivo_acumulado * 100
            def calcular_desvio(real, objetivo_acum):
                if objetivo_acum == 0:
                    return 0
                return round(((real - objetivo_acum) / objetivo_acum * 100), 1)
            
            resultados.append({
                'familia': familia,
                'convencional': {
                    'real': int(real_conv),
                    'objetivo_total': plan_conv,
                    'objetivo_acumulado': objetivo_acum_conv,
                    'desvio': calcular_desvio(real_conv, objetivo_acum_conv)
                },
                'especiales': {
                    'real': int(real_espec),
                    'objetivo_total': plan_espec,
                    'objetivo_acumulado': objetivo_acum_espec,
                    'desvio': calcular_desvio(real_espec, objetivo_acum_espec)
                },
                'tpa': {
                    'real': int(real_tpa),
                    'objetivo_total': plan_tpa,
                    'objetivo_acumulado': objetivo_acum_tpa,
                    'desvio': calcular_desvio(real_tpa, objetivo_acum_tpa)
                },
                'total': {
                    'real': int(real_conv + real_espec + real_tpa),
                    'objetivo_total': plan_conv + plan_espec + plan_tpa,
                    'objetivo_acumulado': objetivo_acum_conv + objetivo_acum_espec + objetivo_acum_tpa,
                    'desvio': calcular_desvio(
                        real_conv + real_espec + real_tpa,
                        objetivo_acum_conv + objetivo_acum_espec + objetivo_acum_tpa
                    )
                }
            })
        
        return jsonify({
            'success': True, 
            'datos': resultados,
            'fecha_calculo': f"{dia_actual}/{mes_actual}/{anio}",
            'porcentaje_acumulado': round(porcentaje_esperado_acumulado, 2),
            'detalles_mensuales': [
                {
                    'mes': mes,
                    'nombre': ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                              'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'][mes-1],
                    'porcentaje': datos_mensuales[mes]['porcentaje'],
                    'dias': datos_mensuales[mes]['dias'],
                    'porcentaje_diario': round(datos_mensuales[mes]['porcentaje'] / datos_mensuales[mes]['dias'], 3)
                }
                for mes in range(1, 13)
            ]
        })
    
    except Exception as e:
        print(f"Error en sales_vs_plan: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    # Para Hugging Face Spaces, usar puerto 7860
    port = int(os.environ.get('PORT', 7860))
    app.run(debug=False, host='0.0.0.0', port=port)
