import pymysql
from datetime import date

# Configuration for database connection
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'root'
DB_NAME = 'autoelite'

# Example data for each table
DATA = {
    "concesionarios": [
        ("Concesionario Central", "Av. Principal 123", "NIF123456"),
        ("Concesionario Norte", "Calle Norte 45", "NIF654321"),
        ("Concesionario Sur", "Calle Sur 78", "NIF987654"),
    ],
    "marcas": [
        ("Toyota", "toyota_logo.png"),
        ("Ford", "ford_logo.png"),
        ("BMW", "bmw_logo.png"),
    ],
    "modelos": [
        ("Corolla", "1.8L", 20000, 1),
        ("Mustang", "3.7L", 35000, 2),
        ("X5", "3.0L", 55000, 3),
    ],
    "vehiculos": [
        ("ABC-123", "Disponible", 1, 1),
        ("DEF-456", "En mantenimiento", 2, 2),
        ("GHI-789", "Vendido", 3, 3),
    ],
    "vendedores": [
        ("Juan Pérez", "12345678A", "987654321", 1),
        ("María Gómez", "87654321B", "987654322", 2),
        ("Carlos Ruiz", "56781234C", "987654323", 3),
    ],
    "clientes": [
        ("Ana", "López", "10111213D", "987654324", "Calle 1", "ana.lopez@example.com", "hashed_password_1"),
        ("Luis", "Martínez", "20131415E", "987654325", "Calle 2", "luis.martinez@example.com", "hashed_password_2"),
        ("Sofía", "Hernández", "30151617F", "987654326", "Calle 3", "sofia.hernandez@example.com", "hashed_password_3"),
    ],
    "ventas": [
        (date(2023, 11, 15), 22000, 1, 1, 1),
        (date(2023, 11, 16), 36000, 2, 2, 2),
        (date(2023, 11, 17), 58000, 3, 3, 3),
    ],
    "postventas": [
        ("Cambio de aceite y filtros", 1),
        ("Revisión general", 2),
        ("Cambio de frenos", 3),
    ],
}


def insert_data():
    try:
        # Connect to the database
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = connection.cursor()

        # Insert data into each table
        for table_name, rows in DATA.items():
            print(f"Inserting data into {table_name}...")
            columns = {
                "concesionarios": "(nombre, direccion, nif)",
                "marcas": "(nombre, logo)",
                "modelos": "(nombre, cilindrada, precio_base, id_marca)",
                "vehiculos": "(matricula, estado, id_modelo, id_concesionario)",
                "vendedores": "(nombre, dni, telefono, id_concesionario)",
                "clientes": "(nombre, apellido, dni, telefono, direccion, email, password)",
                "ventas": "(fecha_venta, precio_final, id_vehiculo, id_cliente, id_vendedor)",
                "postventas": "(descripcion, id_venta)",
            }

            # Prepare the query
            query = f"INSERT INTO {table_name} {columns[table_name]} VALUES ({','.join(['%s'] * len(rows[0]))})"
            cursor.executemany(query, rows)

        # Commit the changes
        connection.commit()
        print("All data inserted successfully!")

    except pymysql.MySQLError as e:
        print(f"Error inserting data: {e}")
    finally:
        if connection:
            cursor.close()
            connection.close()


if __name__ == "__main__":
    insert_data()
