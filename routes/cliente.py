from flask import Blueprint, render_template, request, session, redirect, url_for
from flask_mail import Mail
from db import get_db_connection
from email.message import EmailMessage
import ssl 
import smtplib
cliente = Blueprint('cliente', __name__)

# Configuración del correo
mail = Mail()

@cliente.route('/cliente/dashboard/<int:client_id>', methods=['GET', 'POST'])
def cliente_dashboard(client_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        query_postventa= """
            SELECT descripcion
            FROM postventas 
        """
        
        cursor.execute(query_postventa)
        postventa=cursor.fetchall()
        # Obtener los datos del cliente
        query_cliente = """
            SELECT nombre, apellido, email
            FROM clientes
            WHERE id = %s
        """
        cursor.execute(query_cliente, (client_id,))
        cliente_data = cursor.fetchone()


        # Obtener las ventas asociadas al cliente
        query_ventas = """
            SELECT v.fecha_venta, v.precio_final, ve.matricula, m.nombre AS modelo, ven.nombre AS vendedor, v.estado_pago AS metodo_pago
            FROM ventas v
            JOIN vehiculos ve ON v.id_vehiculo = ve.id
            JOIN modelos m ON ve.id_modelo = m.id
            JOIN vendedores ven ON v.id_vendedor = ven.id
            WHERE v.id_cliente = %s
        """
        cursor.execute(query_ventas, (client_id,))
        ventas = cursor.fetchall()

        print("Ventas recuperadas:", ventas)

    finally:
        cursor.close()
        conn.close()

    return render_template('cliente_dashboard.html', cliente=cliente_data, ventas=ventas,postventa=postventa )

@cliente.route('/cliente/solicitar_servicio/', methods=['POST'])
def solicitar_servicio():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Datos del formulario
    nombre_solicitante = request.form['nombre_solicitante']
    modelo_vehiculo = request.form['modelo_vehiculo']
    kilometraje = request.form['kilometraje']
    servicio = request.form['Servicio_Postventa']
    client_email = request.form['email']

    # Recuperar datos del cliente
    cursor.execute("SELECT id FROM clientes WHERE email = %s", (client_email,))
    cliente_data = cursor.fetchone()
    if not cliente_data:
        raise ValueError("El cliente no existe en la base de datos.")

    email_sender = 'samuel.hurtado0202@gmail.com'
    password = 'zyyf ipxv myup jwcj'
    email_reciver = 'samuel.hurtado0202@gmail.com'

    subject = f"Solicitud de Postventa - Cliente {nombre_solicitante} A nombre de: {nombre_solicitante} Modelo del vehículo: {modelo_vehiculo} Kilometraje: {kilometraje} Por el servicio de: {servicio}"
    body = f""" 
    Solicitud de Postventa:

    A nombre de: {nombre_solicitante}
    Modelo del vehículo: {modelo_vehiculo}
    Kilometraje: {kilometraje}
    Por el servicio de: {servicio}

    Contactar al cliente: {client_email}
    """

    print(body)
    # Enviar correo
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_reciver
    em['Subject'] = subject

    
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com",465,context=context) as smtp:
        smtp.login(email_sender,password)
        smtp.sendmail(email_sender, email_reciver, em.as_string())
        print(f"Se envio con exito{em.as_string()}")
        return redirect(url_for('cliente.cliente_dashboard', client_id=cliente_data))
    
