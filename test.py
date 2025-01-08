import pymysql

# Configuración de la base de datos
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'root'
DB_NAME = 'autoelite'

def test_db_connection():
    try:
        # Establecer conexión a la base de datos
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        print("Conexión a la base de datos exitosa.")

        # Crear un cursor para ejecutar consultas
        cursor = conn.cursor()

        # Consultar los modelos
        cursor.execute("SELECT id, nombre FROM modelos")
        modelos = cursor.fetchall()
        if modelos:
            print("Modelos disponibles:")
            for modelo in modelos:
                print(f"ID: {modelo[0]}, Nombre: {modelo[1]}")
        else:
            print("No se encontraron modelos en la base de datos.")

        # Consultar los concesionarios
        cursor.execute("SELECT id, nombre FROM concesionarios")
        concesionarios = cursor.fetchall()
        if concesionarios:
            print("Concesionarios disponibles:")
            for concesionario in concesionarios:
                print(f"ID: {concesionario[0]}, Nombre: {concesionario[1]}")
        else:
            print("No se encontraron concesionarios en la base de datos.")

    except pymysql.MySQLError as e:
        print(f"Error al conectar a la base de datos: {e}")
    finally:
        # Cerrar conexión
        if conn:
            conn.close()
            print("Conexión a la base de datos cerrada.")

if __name__ == "__main__":
    test_db_connection()
