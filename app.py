from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import os
from werkzeug.utils import secure_filename
import json
from datetime import datetime
from psycopg2 import IntegrityError as PgIntegrityError
from db_config import get_db_connection as get_pg_connection, release_db_connection, init_connection_pool
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SECRET_KEY'] = 'tu-clave-secreta-aqui'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Deshabilitar caché

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


# ==================== RUTAS PRINCIPALES ====================

# Página de inicio (selector de aplicaciones)
@app.route('/')
def home():
    return render_template('home.html')

# Página de TEST
@app.route('/test')
def test_simple():
    return render_template('test_simple.html')

# Aplicación PLANEAMIENTO (requiere contraseña - validación en frontend)
@app.route('/planeamiento')
def planeamiento():
    return render_template('planeamiento.html')

# Aplicación VENTAS
@app.route('/ventas')
def ventas():
    return render_template('ventas.html')

# Aplicación ENTREGAS
@app.route('/entregas')
def entregas():
    return render_template('entregas.html')

@app.route('/entregas/reportes')
def entregas_reportes():
    return render_template('entregas_reportes.html')


# ==================== FUNCIONES DE BASE DE DATOS ====================

def get_db_connection():
    """Crear conexión a la base de datos PostgreSQL"""
    return get_pg_connection()


# Ruta principal - Home
@app.route('/')
def index():
    return render_template('index.html')


# Módulo 1: Lista de precios
@app.route('/modulo1')
def modulo1():
    return render_template('modulo1.html')

# API para obtener precios
@app.route('/api/precios', methods=['GET'])
def get_precios():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT modelo, precio_ars, precio_usd, cotizacion, descuento, visible, dado_baja, familia FROM precios ORDER BY familia, modelo')
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
def save_precios():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Actualizar precios
        for modelo in data.get('modelos', []):
            cursor.execute('''
                UPDATE precios 
                SET precio_ars = %s, precio_usd = %s, cotizacion = %s, descuento = %s, dado_baja = %s, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE modelo = %s
            ''', (modelo['precio_ars'], modelo['precio_usd'], modelo['cotizacion'], modelo['descuento'], modelo.get('dado_baja', 0), modelo['nombre']))
        
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
def modulo2():
    return render_template('modulo2.html')


# ==================== API MÓDULO 2: PREVENTA ====================

# API para obtener preventa
@app.route('/api/preventa', methods=['GET'])
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
            
            # Calcular precio con descuento
            precio = 0
            if modelo in precios_data:
                precio_base = precios_data[modelo]['precio_ars']
                descuento = precios_data[modelo]['descuento']
                if descuento > 0:
                    precio = precio_base * (1 - descuento / 100)
                else:
                    precio = precio_base
            
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
def modulo3():
    return render_template('modulo3.html')


@app.route('/procesar_excel', methods=['POST'])
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
        
        # Mantener solo las primeras 15 columnas
        df = df.iloc[:, :15]
        
        # **NUEVO: Obtener precios de la base de datos y hacer match con Modelo/Versión**
        if 'Modelo/Versión' in df.columns and 'Precio p/ Disponible' in df.columns:
            print("🔄 Haciendo match de precios desde la base de datos...")
            
            # Obtener todos los precios y descuentos de la base de datos
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT modelo, precio_ars, descuento FROM precios')
            precios_data = {}
            for row in cursor.fetchall():
                precios_data[row['modelo']] = {
                    'precio_ars': row['precio_ars'],
                    'descuento': row['descuento']
                }
            conn.rollback()
            release_db_connection(conn)
            
            print(f"📊 Precios cargados: {len(precios_data)} modelos")
            
            # Aplicar precios con descuento a la columna "Precio p/ Disponible"
            def get_precio_con_descuento(modelo):
                if pd.isna(modelo):
                    return 0
                modelo_str = str(modelo).strip()
                # Buscar coincidencia exacta
                if modelo_str in precios_data:
                    precio = precios_data[modelo_str]['precio_ars']
                    descuento = precios_data[modelo_str]['descuento']
                    # Aplicar descuento si existe
                    if descuento > 0:
                        precio_final = precio * (1 - descuento / 100)
                        return precio_final
                    return precio
                # Si no hay coincidencia, devolver 0
                return 0
            
            df['Precio p/ Disponible'] = df['Modelo/Versión'].apply(get_precio_con_descuento)
            
            # Contar cuántos precios se encontraron
            precios_encontrados = (df['Precio p/ Disponible'] > 0).sum()
            print(f"✅ Precios aplicados: {precios_encontrados} de {len(df)} registros")
        
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
def modulo4():
    return render_template('modulo4.html')


@app.route('/modulo5')
def modulo5():
    return render_template('modulo5.html')


@app.route('/modulo6')
def modulo6():
    return render_template('modulo6.html')

@app.route('/test_zonas')
def test_zonas():
    return send_file('test_zona_logica.html')


# ==================== API MÓDULO 4: DISPONIBLES ====================

# API para obtener unidades disponibles
@app.route('/api/disponibles', methods=['GET'])
def get_disponibles():
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
               p.familia, p.descuento as descuento_individual
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
        precio_base = row['precio_disponible'] or 0
        descuento_total = 0
        detalles_descuento = []
        
        # Descuento por Stock
        ubicacion_actual = (row['ubicacion'] or '').strip().upper()
        desc_stock = descuentos_config.get('stock', {}).get('descuento_stock', 0)
        
        # Comparar si contiene "STOCK" en cualquier parte
        if 'STOCK' in ubicacion_actual and desc_stock > 0:
            descuento_total += desc_stock
            detalles_descuento.append(f"Stock: {desc_stock}%")
            print(f"✅ Descuento Stock aplicado: {desc_stock}% a {row['numero_fabrica']} (Ubicación: {row['ubicacion']})")
        
        # Descuento por Color - Normalizar para comparar
        color_original = (row['color'] or '').strip()
        # Normalizar: quitar espacios, pasar a minúsculas y reemplazar espacios por _
        color_normalizado = color_original.lower().replace(' ', '_')
        desc_color = descuentos_config.get('color', {}).get(color_normalizado, 0)
        if desc_color > 0:
            descuento_total += desc_color
            detalles_descuento.append(f"Color: {desc_color}%")
            print(f"✅ Descuento Color aplicado: {desc_color}% a {row['numero_fabrica']} (Color: {color_original})")
        
        # Descuento por Antigüedad
        if row['entrega_estimada']:
            try:
                # Intentar parsear diferentes formatos de fecha
                fecha_str = row['entrega_estimada']
                fecha_entrega = None
                
                # Intentar formato ISO (YYYY-MM-DD)
                try:
                    fecha_entrega = datetime.strptime(fecha_str, '%Y-%m-%d')
                except:
                    # Intentar formato con día de la semana (Mon, DD MMM YYYY HH:MM:SS GMT)
                    try:
                        # Remover GMT y parsear
                        if 'GMT' in fecha_str:
                            fecha_str_limpia = fecha_str.replace(' GMT', '').strip()
                            fecha_entrega = datetime.strptime(fecha_str_limpia, '%a, %d %b %Y %H:%M:%S')
                        else:
                            # Intentar otros formatos comunes
                            fecha_entrega = datetime.fromisoformat(fecha_str.replace('GMT', '').strip())
                    except:
                        pass
                
                if fecha_entrega:
                    meses_config = descuentos_config.get('antiguedad', {}).get('meses', 3)
                    desc_antiguedad = descuentos_config.get('antiguedad', {}).get('descuento', 0)
                    fecha_limite = datetime.now() - relativedelta(months=int(meses_config))
                    
                    if fecha_entrega < fecha_limite and desc_antiguedad > 0:
                        descuento_total += desc_antiguedad
                        detalles_descuento.append(f"Antigüedad: {desc_antiguedad}%")
                        print(f"✅ Descuento Antigüedad aplicado: {desc_antiguedad}% a {row['numero_fabrica']} (Entrega: {fecha_entrega.date()})")
            except Exception as e:
                print(f"❌ Error procesando fecha para {row['numero_fabrica']}: {e}")
        
        # Calcular precio final
        precio_final = precio_base * (1 - descuento_total / 100)
        
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
            'precio_disponible': precio_final,
            'precio_base': precio_base,
            'descuento_individual': row['descuento_individual'] or 0,
            'descuento_adicional': descuento_total,
            'detalles_descuento': ', '.join(detalles_descuento) if detalles_descuento else 'Sin descuentos adicionales',
            'cod_cliente': row['cod_cliente'],
            'cliente': row['cliente'],
            'vendedor': row['vendedor'],
            'operacion': row['operacion'],
            'familia': row['familia'] or 'SIN FAMILIA'
        })
    
    return jsonify(disponibles)

# API para guardar/reemplazar unidades disponibles
@app.route('/api/disponibles', methods=['POST'])
def save_disponibles():
    data = request.json
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
                    cod_cliente, cliente, vendedor, operacion
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                item.get('operacion')
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
def get_unidades_reservadas():
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
def add_unidad_reservada():
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
def delete_unidad_reservada(numero_fabrica):
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
def get_recaudacion():
    """Obtener datos de recaudación separados por Stock y No Stock"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Obtener unidades reservadas
    cursor.execute('SELECT numero_fabrica FROM unidades_reservadas')
    reservadas = [row['numero_fabrica'] for row in cursor.fetchall()]
    
    # Obtener todas las unidades disponibles
    cursor.execute('''
        SELECT 
            numero_fabrica,
            modelo_version,
            ubicacion,
            precio_disponible
        FROM disponibles
    ''')
    
    disponibles = cursor.fetchall()
    release_db_connection(conn)
    
    # Filtrar unidades reservadas
    disponibles_filtrados = [d for d in disponibles if d['numero_fabrica'] not in reservadas]
    
    # Separar por Stock y No Stock
    en_stock = []
    no_stock = []
    
    for unidad in disponibles_filtrados:
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


if __name__ == '__main__':
    # Para Hugging Face Spaces, usar puerto 7860
    port = int(os.environ.get('PORT', 7860))
    app.run(debug=False, host='0.0.0.0', port=port)
