from flask import Blueprint, redirect, render_template, request, url_for, flash
from flask.json import jsonify
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash
from db import get_db_connection
import pymysql
# Crear un Blueprint para las rutas de administrador
admin = Blueprint('admin', __name__)

# Decorador para verificar que el usuario es administrador
def admin_required(func):
    from functools import wraps

    @wraps(func)
    @login_required
    def wrapper(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Acceso denegado: No tienes permisos de administrador.', 'danger')
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return wrapper

# Ruta para gestionar el inventario

@admin.route('/inventario', methods=['GET'])
def gestionar_inventario():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Consultar vehículos con sus nombres de modelo
        query = """
            SELECT ve.id, mo.nombre AS modelo_nombre, ve.matricula, ve.estado
            FROM vehiculos ve
            JOIN modelos mo ON ve.id_modelo = mo.id
        """
        cursor.execute(query)
        vehiculos = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    return render_template('admin_inventario.html', vehiculos=vehiculos)
# Ruta para agregar un vehículo

@admin.route('/inventario/agregar', methods=['GET', 'POST'])
def agregar_vehiculo():
    conn = get_db_connection()
    cursor = conn.cursor()

    
    cursor.execute("SELECT id, nombre FROM modelos")
    modelos = cursor.fetchall() 

    cursor.execute("SELECT id, nombre FROM concesionarios")
    concesionarios = cursor.fetchall()  

    if request.method == 'POST':
        matricula = request.form['matricula']
        estado = request.form['estado']
        id_modelo = request.form['id_modelo']
        id_concesionario = request.form['id_concesionario']

        try:
            # Insert vehicle into the database
            query = """
                INSERT INTO vehiculos (matricula, estado, id_modelo, id_concesionario)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (matricula, estado, id_modelo, id_concesionario))
            conn.commit()

            flash('Vehículo agregado exitosamente', 'success')
            return redirect(url_for('admin.gestionar_inventario')) 
        except Exception as e:
            conn.rollback()
            flash(f'Error al agregar el vehículo: {str(e)}', 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template('admin_agregar_vehiculo.html', modelos=modelos, concesionarios=concesionarios)

# Ruta para eliminar un vehículo
@admin.route('/inventario/eliminar/<int:id_vehiculo>', methods=['POST'])
def eliminar_vehiculo(id_vehiculo):
    """Permite al administrador eliminar un vehículo del inventario"""
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            query = "DELETE FROM vehiculos WHERE id = %s"
            cursor.execute(query, (id_vehiculo,))
            connection.commit()
        flash('Vehículo eliminado correctamente', 'success')
        return redirect(url_for('admin.gestionar_inventario'))
    except Exception as e:
        flash(f'Error al eliminar el vehículo: {str(e)}', 'danger')
    finally:
        connection.close()

    return redirect(url_for('admin.gestionar_inventario'))



# Ruta para gestionar usuarios
@admin.route('/usuarios', methods=['GET'])
#@admin_required
def gestionar_usuarios():
    """Muestra la lista de usuarios y permite gestionar sus roles y permisos"""

    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users")
        usuarios = cursor.fetchall()
    connection.close()
    return render_template('admin_usuarios.html', usuarios=usuarios)
    
    

# Ruta para crear un nuevo usuario
@admin.route('/usuarios/crear', methods=['GET', 'POST'])
#@admin_required
def crear_usuario():
    """Permite al administrador crear un nuevo usuario."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Obtener concesionarios para el dropdown
    cursor.execute("SELECT id, nombre FROM concesionarios")
    concesionarios = cursor.fetchall()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        nombre = request.form['nombre']
        dni = request.form['dni']
        telefono = request.form['telefono']
        id_concesionario = request.form['id_concesionario']
        
        # Hashear la contraseña
        password_hashed = generate_password_hash(password, method='sha256')

        try:
            # Validar si el usuario ya existe
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            existing_user = cursor.fetchone()
            if existing_user:
                print(f"Error: El usuario {username} ya existe.")
                return render_template('admin_crear_usuario.html', concesionarios=concesionarios)

            # Insertar en la tabla `users`
            cursor.execute("""
                INSERT INTO users (username, password_hash, role)
                VALUES (%s, %s, %s)
            """, (username, password_hashed, role))

            # Insertar en la tabla `vendedor`
            cursor.execute("""
                INSERT INTO vendedores (nombre, dni, telefono, id_concesionario)
                VALUES (%s, %s, %s, %s)
            """, (nombre, dni, telefono, id_concesionario))

            conn.commit()
            print("Usuario creado correctamente")
            return redirect(url_for('admin.gestionar_usuarios'))
        except Exception as e:
            conn.rollback()
            print(f"Error al crear el usuario: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    return render_template('admin_crear_usuario.html', concesionarios=concesionarios)

# Ruta para actualizar el rol de un usuario
@admin.route('/usuarios/usuarios/<int:id_usuario>', methods=[ 'POST'])
def actualizar_rol_usuario(id_usuario):
    """Permite al administrador actualizar el rol de un usuario"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar si el usuario existe
    cursor.execute("SELECT * FROM users WHERE id = %s", (id_usuario,))
    usuario = cursor.fetchone()

    if not usuario:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('admin.gestionar_usuarios'))

    if request.method == 'POST':
        if usuario['role'] == 'admin':
            cursor.execute("UPDATE users SET role = %s WHERE id = %s", ('vendedor', id_usuario))
            conn.commit()
            conn.close()
            flash('Rol actualizado correctamente', 'success')
            return redirect(url_for('admin.gestionar_usuarios'))
        elif usuario['role'] == 'vendedor':
            cursor.execute("UPDATE users SET role = %s WHERE id = %s", ('admin', id_usuario))
            conn.commit()
            conn.close()
            flash('Rol actualizado correctamente', 'success')
            return redirect(url_for('admin.gestionar_usuarios'))

    conn.close()
    return render_template('admin_actualizar_rol.html', usuario=usuario)


@admin.route('/ventas', methods=['GET'])
def ver_ventas():
    """Muestra la lista de todas las ventas realizadas o filtradas por vendedor o cliente"""
    connection = get_db_connection()
    filter_by = request.args.get('filter_by')
    filter_value = request.args.get('filter_value')

    query = """
        SELECT v.id AS venta_id, 
               v.fecha_venta, 
               v.precio_final,
               v.estado_pago, 
               ve.matricula AS vehiculo_matricula, 
               c.nombre AS cliente_nombre, 
               CONCAT(c.nombre, ' ', c.apellido) AS cliente_completo, 
               ven.nombre AS vendedor_nombre
        FROM ventas v
        JOIN vehiculos ve ON v.id_vehiculo = ve.id
        JOIN clientes c ON v.id_cliente = c.id
        JOIN vendedores ven ON v.id_vendedor = ven.id
    """

    # Añadir condiciones de filtro si es necesario
    if filter_by and filter_value:
        if filter_by == 'vendedor':
            query += " WHERE ven.nombre LIKE %s"
        elif filter_by == 'cliente':
            query += " WHERE CONCAT(c.nombre, ' ', c.apellido) LIKE %s"
        filter_value = f"%{filter_value}%"  # Búsqueda parcial

    with connection.cursor() as cursor:
        if filter_by and filter_value:
            cursor.execute(query, (filter_value,))
        else:
            cursor.execute(query)
        ventas = cursor.fetchall()
    connection.close()

    return render_template('admin_ventas.html', ventas=ventas)

@admin.route('/generar_venta', methods=['GET', 'POST'])
def generar_venta():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Obtener vendedores y vehículos disponibles para los dropdowns
    cursor.execute("""
        SELECT v.matricula, v.id AS id_vehiculo, m.nombre AS nombre_modelo, m.id AS id_modelo
        FROM vehiculos v
        JOIN modelos m ON v.id_modelo = m.id
        WHERE v.estado != 'vendido'
    """)
    vehiculos_disponibles = cursor.fetchall()

    cursor.execute("SELECT id, nombre FROM vendedores")
    vendedores = cursor.fetchall()

    if request.method == 'POST':
        # Datos del cliente
        nombre_cliente = request.form['nombre_cliente']
        apellido_cliente = request.form['apellido_cliente']
        dni_cliente = request.form['dni_cliente']
        telefono_cliente = request.form['telefono_cliente']
        direccion_cliente = request.form['direccion_cliente']
        email_cliente = request.form['email']
        password_cliente = dni_cliente  # Usar el DNI como contraseña inicial

        # Hashear la contraseña
        password_hashed = generate_password_hash(password_cliente)

        # Datos de la venta
        matricula_vehiculo = request.form['id_matricula']
        id_vendedor = request.form['id_vendedor']
        metodo_pago = request.form['metodo_pago']
        precio_final = request.form['precio_final']

        try:
            print("Datos recibidos:", request.form)

            # Recuperar `id_vehiculo` y `id_modelo` a partir de la matrícula seleccionada
            cursor.execute("""
                SELECT id AS id_vehiculo 
                FROM vehiculos 
                WHERE matricula = %s
            """, (matricula_vehiculo,))
            vehiculo_data = cursor.fetchone()

            if not vehiculo_data:
                raise ValueError(f"No se encontró un vehículo con matrícula {matricula_vehiculo}")

            id_vehiculo = vehiculo_data['id_vehiculo']
            

            # Insertar cliente en la base de datos
            cursor.execute("""
                INSERT INTO clientes (nombre, apellido, dni, telefono, direccion, email, password)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (nombre_cliente, apellido_cliente, dni_cliente, telefono_cliente, direccion_cliente, email_cliente, password_hashed))
            id_cliente = cursor.lastrowid
            print(id_cliente)

            # Insertar venta en la base de datos
            cursor.execute("""
                INSERT INTO ventas (fecha_venta, precio_final, id_vehiculo, id_cliente, id_vendedor, estado_pago, matricula_vehiculo)
                VALUES (NOW(), %s, %s, %s, %s, %s, %s)
            """, (precio_final, id_vehiculo, id_cliente, id_vendedor, metodo_pago, matricula_vehiculo))

            # Actualizar el estado del vehículo a "vendido"
            cursor.execute("""
                UPDATE vehiculos
                SET estado = 'vendido'
                WHERE matricula = %s
            """, (matricula_vehiculo,))

            conn.commit()
            print('Venta registrada exitosamente y vehículo actualizado a "vendido".')
            return redirect(url_for('admin.ver_ventas'))
        except Exception as e:
            print(f"Error al procesar el formulario: {str(e)}")
            conn.rollback()
            return redirect(url_for('admin.generar_venta'))
        finally:
            cursor.close()
            conn.close()

    return render_template('generar_venta.html', vendedores=vendedores, vehiculos=vehiculos_disponibles)


