from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Importar los modelos para registrarlos
from .models import User, Concesionario, Marca, Modelo, Vehiculo, Vendedor, Cliente, Venta, Postventa
