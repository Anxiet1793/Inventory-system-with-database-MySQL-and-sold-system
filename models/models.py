from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Inicializa SQLAlchemy (asegúrate de inicializar esto desde app.py correctamente)
db = SQLAlchemy()

# Modelo para usuarios
class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    def set_password(self, password):
        """Genera un hash para la contraseña"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica si la contraseña es correcta"""
        return check_password_hash(self.password_hash, password)


# Modelo para concesionarios
class Concesionario(db.Model):
    __tablename__ = 'concesionarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(255))
    nif = db.Column(db.String(50), nullable=False)


# Modelo para marcas
class Marca(db.Model):
    __tablename__ = 'marcas'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    logo = db.Column(db.String(255))


# Modelo para modelos de vehículos
class Modelo(db.Model):
    __tablename__ = 'modelos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    cilindrada = db.Column(db.String(50))
    precio_base = db.Column(db.Numeric(10, 2), nullable=False)
    id_marca = db.Column(db.Integer, db.ForeignKey('marcas.id'))

    marca = db.relationship('Marca', backref='modelos')


# Modelo para vehículos
class Vehiculo(db.Model):
    __tablename__ = 'vehiculos'

    id = db.Column(db.Integer, primary_key=True)
    matricula = db.Column(db.String(50), unique=True, nullable=False)
    estado = db.Column(db.String(50))
    id_modelo = db.Column(db.Integer, db.ForeignKey('modelos.id'))
    id_concesionario = db.Column(db.Integer, db.ForeignKey('concesionarios.id'))

    modelo = db.relationship('Modelo', backref='vehiculos')
    concesionario = db.relationship('Concesionario', backref='vehiculos')


# Modelo para vendedores
class Vendedor(db.Model):
    __tablename__ = 'vendedores'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(50), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    id_concesionario = db.Column(db.Integer, db.ForeignKey('concesionarios.id'))

    concesionario = db.relationship('Concesionario', backref='vendedores')


# Modelo para clientes
class Cliente(db.Model):
    __tablename__ = 'clientes'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(50), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.String(255))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        """Genera un hash para la contraseña"""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Verifica si la contraseña es correcta"""
        return check_password_hash(self.password, password)


# Modelo para ventas
class Venta(db.Model):
    __tablename__ = 'ventas'

    id = db.Column(db.Integer, primary_key=True)
    fecha_venta = db.Column(db.Date, nullable=False)
    precio_final = db.Column(db.Numeric(10, 2), nullable=False)
    id_vehiculo = db.Column(db.Integer, db.ForeignKey('vehiculos.id'))
    id_cliente = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    id_vendedor = db.Column(db.Integer, db.ForeignKey('vendedores.id'))

    vehiculo = db.relationship('Vehiculo', backref='ventas')
    cliente = db.relationship('Cliente', backref='ventas')
    vendedor = db.relationship('Vendedor', backref='ventas')


# Modelo para postventas
class Postventa(db.Model):
    __tablename__ = 'postventas'

    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.Text)
    id_venta = db.Column(db.Integer, db.ForeignKey('ventas.id'))

    venta = db.relationship('Venta', backref='postventas')
