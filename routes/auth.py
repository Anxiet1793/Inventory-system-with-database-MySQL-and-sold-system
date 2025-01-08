from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import UserMixin, login_user, logout_user
from werkzeug.security import check_password_hash
from db import get_db_connection

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form.get('username')  # Use .get() to avoid KeyError
        password = request.form.get('password')

        if not username_or_email or not password:
            print('Missing username or password in form submission')
            return render_template('login.html')  # Reload the login page

        # Rest of your login logic goes here


        # Special case for admin/admin login
        if username_or_email == 'admin' and password == 'admin':
            class AdminUser(UserMixin):
                id = 1
                username = 'admin'
                role = 'admin'

            admin_user = AdminUser()
            login_user(admin_user)
            print('Inicio de sesión como administrador exitoso')
            return redirect(url_for('admin.gestionar_inventario'))

        # Check user in the database
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Query the `users` table (renamed from `usuarios`)
            query_users = """
                SELECT id, username, password_hash, role 
                FROM users 
                WHERE username = %s
            """
            cursor.execute(query_users, (username_or_email,))
            user_data = cursor.fetchone()

            if not user_data:
                # If not found in `users`, search in `clientes` by email
                query_clients = """
                    SELECT id, email, password 
                    FROM clientes 
                    WHERE email = %s
                """
                cursor.execute(query_clients, (username_or_email,))
                client_data = cursor.fetchone()

                # Debugging: Check retrieved client data
                print("Datos recuperados de clientes:", client_data)

                if client_data:
                    # Validate password
                    if check_password_hash(client_data['password'], password):
                        # If it's a client, create a session
                        class ClientUser(UserMixin):
                            pass

                        user = ClientUser()
                        user.id = client_data['id']
                        user.username = client_data['email']  # Email as username
                        user.role = 'cliente'
                        client_id=(client_data['id'])
                        login_user(user)
                        print('Inicio de sesión exitoso como cliente')
                        return redirect(url_for('cliente.cliente_dashboard', client_id=(client_data['id']) ))  # Redirect to client dashboard
                    else:
                        print('Contraseña incorrecta para el cliente')
                else:
                    print('Cliente no encontrado en la base de datos')
                    return redirect(url_for('auth.login'))

            # If found in `users`, validate the password
            if check_password_hash(user_data['password_hash'], password):
                class User(UserMixin):
                    pass

                user = User()
                user.id = user_data['id']
                user.username = user_data['username']
                user.role = user_data['role']

                login_user(user)
                print('Inicio de sesión exitoso')

                # Redirect based on role
                if user.role == 'admin':
                    return redirect(url_for('admin.gestionar_inventario'))
                elif user.role == 'vendedor':
                    return redirect(url_for('vendedor.generar_venta'))  # Redirect to sales generation form
                else:
                    print('No se reconoce el rol de usuario')
                    return redirect(url_for('auth.login'))
            else:
                print('Usuario o contraseña incorrectos')
        except Exception as e:
            print(f'Ocurrió un error al intentar iniciar sesión: {e}')
        finally:
            cursor.close()
            conn.close()

    return render_template('login.html')



@auth.route('/logout')
def logout():
    logout_user()
    print('Has cerrado sesión exitosamente')
    return redirect(url_for('auth.login'))
