import pg8000
from django.conf import settings
import base64

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

def obtener_gerencias():
    conexion = conectar()
    if not conexion:
        return []

    try:
        cursor = conexion.cursor()
        query = "SELECT id, nombre FROM Gerencia"  
        cursor.execute(query)
        gerencias = cursor.fetchall()
        cursor.close()
        conexion.close()
        return gerencias
    except Exception as e:
        print(f"Error al obtener gerencias: {e}")
        return []

def almacenar_asignacion(codigo, fecha_asignacion, gerencia_id, qr_code):
    conexion = conectar()
    if not conexion:
        return False

    try:
        cursor = conexion.cursor()
        query = """
        INSERT INTO Asignacion (codigo, fecha_asignacion, gerencia_id, qr_code)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (codigo, fecha_asignacion, gerencia_id, qr_code))
        conexion.commit()
        cursor.close()
        conexion.close()
        return True
    except Exception as e:
        print(f"Error al almacenar la asignación: {e}")
        return False

def obtener_productos():
    conexion = conectar()
    if not conexion:
        return []

    try:
        cursor = conexion.cursor()
        query = """
        SELECT r.id_registro, r.producto, m.nombre AS marca, r.descripcion, r.color, g.nombre AS gerencia, r.fecha_registro
        FROM Registro r
        JOIN Marca m ON r.marca = m.id
        JOIN Gerencia g ON r.gerencia = g.id
        """
        cursor.execute(query)
        productos = cursor.fetchall()
        cursor.close()
        conexion.close()
        return productos
    except Exception as e:
        print(f"Error al obtener productos: {e}")
        return []
    
def Consulta_Bienes_Asignados():
    conexion = conectar()
    if not conexion:
        return []

    try:
        cursor = conexion.cursor()
        query = """
        SELECT a.id, a.codigo, a.fecha_Asignacion, g.nombre AS gerencia, a.qr_code FROM asignacion a 
        JOIN gerencia g ON a.gerencia_id = g.id
        """
        cursor.execute(query)
        asignaciones = cursor.fetchall()
        cursor.close()
        conexion.close()
        asignaciones_convertidas = [] 
        for asignacion in asignaciones: 
            asignacion_convertida = list(asignacion) 
            if asignacion_convertida[4]: 
                asignacion_convertida[4] = base64.b64encode(asignacion_convertida[4]).decode('utf-8') 
                asignaciones_convertidas.append(asignacion_convertida) 
        return asignaciones_convertidas
    except Exception as e:
        print(f"Error al obtener asiganciones: {e}")
        return []

def consulta_disponibles():
    conexion = conectar()
    if not conexion:
        return []

    try:
        cursor = conexion.cursor()
        query = """SELECT r.Id_Registro, m.Nombre AS Marca, r.Producto, r.Color, r.Serial, r.Fecha_Registro, 
        c.categoria AS Categoria, r.Foto, r.Cantidad FROM Registro r 
        JOIN Marca m ON r.Marca = m.Id
        JOIN Categoria c ON r.Categoria = c.Id;"""  
        cursor.execute(query)
        disponibles = cursor.fetchall()
        cursor.close()
        conexion.close()
        return disponibles
    except Exception as e:
        print(f"Error al obtener Bienes Disponibles: {e}")
        return []

def consulta_desincorporacion():
    conexion = conectar()
    if not conexion:
        return []

    try:
        cursor = conexion.cursor()
        query = """SELECT 
        d.Id_Des, 
        a.codigo AS codigo_bien, 
        g.nombre AS Gerencia, 
        a.fecha_Asignacion,
        d.motivo_retiro,
        d.fecha_retiro,
        a.qr_code, 
        (al.estado || ', ' || al.municipio || ', ' || al.parroquia || ', ' || al.lugar) AS Ubicacion_Final 
        FROM 
        Desincorporacion d 
        JOIN 
        Asignacion a ON d.Bien_Retirar = a.Id 
        JOIN 
        Gerencia g ON a.gerencia_id = g.id
        JOIN 
        Almacen al ON CAST(d.ubicación_final AS INTEGER) = al.id;"""  
        cursor.execute(query)
        desincorporacion= cursor.fetchall()
        cursor.close()
        conexion.close()
        return desincorporacion
    except Exception as e:
        print(f"Error al obtener Bienes desincorporados: {e}")
        return []

def obtener_categorias():
    conexion = conectar()
    if not conexion:
        return []

    try:
        cursor = conexion.cursor()
        query = "SELECT id, categoria FROM categoria"  
        cursor.execute(query)
        categorias = cursor.fetchall()
        cursor.close()
        conexion.close()
        return categorias
    except Exception as e:
        print(f"Error al obtener categorias: {e}")
        return []
    
def obtener_marcas():
    conexion = conectar()
    if not conexion:
        return []

    try:
        cursor = conexion.cursor()
        query = "SELECT id, nombre FROM marca"  
        cursor.execute(query)
        marcas = cursor.fetchall()
        cursor.close()
        conexion.close()
        return marcas
    except Exception as e:
        print(f"Error al obtener marcas: {e}")
        return []