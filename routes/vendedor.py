from functools import wraps
from flask import Blueprint, redirect, render_template, request, url_for, flash
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash
from db import get_db_connection
# Crear un Blueprint para las rutas de vendedor
vendedor = Blueprint('vendedor', __name__)

# Verificar que el usuario es vendedor
def vendedor_required(func):
    @wraps(func)
    @login_required
    def wrapper(*args, **kwargs):
        if current_user.role != 'vendedor':
            flash('Acceso denegado: No tienes permisos de vendedor.', 'danger')
            return redirect(url_for('auth.login'))
        return func(*args, **kwargs)
    return wrapper

#@vendedor.route('/dashboard', methods=['GET'])
#@vendedor_required
#def vendedor_dashboard():
#    """Dashboard principal para los vendedores"""
#    return render_template('vendedor_dashboard.html')

@vendedor.route('/inventario', methods=['GET'])
def ver_inventario():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        flash('Mostrando inventario', 'error')
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

    return render_template('vendedor_inventario.html', vehiculos=vehiculos)
@vendedor.route('/generar_venta', methods=['GET', 'POST'])
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
            return redirect(url_for('vendedor.inventario'))
        except Exception as e:
            print(f"Error al procesar el formulario: {str(e)}")
            conn.rollback()
            return redirect(url_for('vendedor.generar_venta'))
        finally:
            cursor.close()
            conn.close()

    return render_template('generar_venta.html', vendedores=vendedores, vehiculos=vehiculos_disponibles)