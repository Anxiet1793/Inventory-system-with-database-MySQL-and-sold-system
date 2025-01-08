import pymysql

# Configuración de la conexión a la base de datos
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'root'
DB_NAME = 'autoelite'

# Consultas para crear las tablas
TABLES = {
    "users": """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(150) NOT NULL UNIQUE,
            password_hash VARCHAR(150) NOT NULL,
            role VARCHAR(50) NOT NULL
        );
    """,
    "concesionarios": """
        CREATE TABLE IF NOT EXISTS concesionarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            direccion VARCHAR(255),
            nif VARCHAR(50) NOT NULL
        );
    """,
    "marcas": """
        CREATE TABLE IF NOT EXISTS marcas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            logo VARCHAR(255)
        );
    """,
    "modelos": """
        CREATE TABLE IF NOT EXISTS modelos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            cilindrada VARCHAR(50),
            precio_base DECIMAL(10, 2) NOT NULL,
            id_marca INT NOT NULL,
            FOREIGN KEY (id_marca) REFERENCES marcas(id) ON DELETE CASCADE
        );
    """,
    "vehiculos": """
        CREATE TABLE IF NOT EXISTS vehiculos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            matricula VARCHAR(50) NOT NULL UNIQUE,
            estado VARCHAR(50),
            id_modelo INT NOT NULL,
            id_concesionario INT NOT NULL,
            FOREIGN KEY (id_modelo) REFERENCES modelos(id) ON DELETE CASCADE,
            FOREIGN KEY (id_concesionario) REFERENCES concesionarios(id) ON DELETE CASCADE
        );
    """,
    "vendedores": """
        CREATE TABLE IF NOT EXISTS vendedores (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            dni VARCHAR(50) NOT NULL UNIQUE,
            telefono VARCHAR(20),
            id_concesionario INT NOT NULL,
            FOREIGN KEY (id_concesionario) REFERENCES concesionarios(id) ON DELETE CASCADE
        );
    """,
    "clientes": """
        CREATE TABLE IF NOT EXISTS clientes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            apellido VARCHAR(100) NOT NULL,
            dni VARCHAR(50) NOT NULL UNIQUE,
            telefono VARCHAR(20),
            direccion VARCHAR(255),
            email VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(150) NOT NULL
        );
    """,
    "ventas": """
        CREATE TABLE IF NOT EXISTS ventas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            fecha_venta DATE NOT NULL,
            precio_final DECIMAL(10, 2) NOT NULL,
            id_vehiculo INT NOT NULL,
            id_cliente INT NOT NULL,
            id_vendedor INT NOT NULL,
            FOREIGN KEY (id_vehiculo) REFERENCES vehiculos(id) ON DELETE CASCADE,
            FOREIGN KEY (id_cliente) REFERENCES clientes(id) ON DELETE CASCADE,
            FOREIGN KEY (id_vendedor) REFERENCES vendedores(id) ON DELETE CASCADE
        );
    """,
    "postventas": """
        CREATE TABLE IF NOT EXISTS postventas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            descripcion TEXT,
            id_venta INT NOT NULL,
            FOREIGN KEY (id_venta) REFERENCES ventas(id) ON DELETE CASCADE
        );
    """
}

# Función para crear las tablas
def create_tables():
    try:
        # Conectar a la base de datos
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = connection.cursor()

        # Crear las tablas
        for table_name, create_query in TABLES.items():
            print(f"Creando tabla {table_name}...")
            cursor.execute(create_query)

        # Confirmar cambios
        connection.commit()
        print("¡Todas las tablas se han creado correctamente!")

    except pymysql.MySQLError as e:
        print(f"Error al crear las tablas: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()

# Ejecutar la creación de las tablas
if __name__ == "__main__":
    create_tables()
