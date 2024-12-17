import pg8000
from django.conf import settings

db_config = {
    'database': settings.DATABASES['default']['NAME'],
    'user': settings.DATABASES['default']['USER'],
    'password': settings.DATABASES['default']['PASSWORD'],
    'host': settings.DATABASES['default']['HOST'],
    'port': settings.DATABASES['default']['PORT']
}

def conectar():
    try:
        conexion = pg8000.connect(**db_config)
        return conexion
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

def validar_usuario(usuario, contrasena):
    conexion = conectar()
    if not conexion:
        return False

    try:
        cursor = conexion.cursor()
        query = "SELECT 1 FROM usuarios WHERE usuario = %s AND contrasena = %s"
        cursor.execute(query, (usuario, contrasena))
        result = cursor.fetchone()
        cursor.close()
        conexion.close()
        return result is not None
    except Exception as e:
        print(f"Error al validar usuario: {e}")
        return False
