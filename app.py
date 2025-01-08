from flask import Flask
from flask_login import LoginManager
from routes.auth import auth as auth_blueprint
from routes.admin import admin as admin_blueprint
from routes.vendedor import vendedor as vendedor_blueprint
from routes.cliente import cliente as cliente_blueprint
from config import SECRET_KEY
from db import get_db_connection
# Inicializar la aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

# Inicializar el gestor de login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

# Cargar el usuario (usado por Flask-Login)
@login_manager.user_loader
def load_user(user_id):
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
        return user
    finally:
        connection.close()

# Registrar Blueprints después de inicializar completamente la app
app.register_blueprint(auth_blueprint)
app.register_blueprint(admin_blueprint, url_prefix='/admin')
app.register_blueprint(vendedor_blueprint, url_prefix='/vendedor')
app.register_blueprint(cliente_blueprint, url_prefix='/cliente')

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)
