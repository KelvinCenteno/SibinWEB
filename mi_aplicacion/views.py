import json
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .db import validar_usuario, obtener_gerencias, almacenar_asignacion, obtener_productos, Consulta_Bienes_Asignados, consulta_disponibles
import qrcode
from io import BytesIO
import base64
from django.conf import settings 
import os
from .generar_informe import completar_plantilla
import requests
from datetime import datetime
def index(request):
    return render(request, 'login.html')

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        datos = json.loads(request.body)
        usuario = datos.get('usuario').strip()
        contrasena = datos.get('contrasena').strip()
        if validar_usuario(usuario, contrasena):
            request.session['usuario'] = usuario  # Guardar el usuario en la sesión
            return JsonResponse({'status': 'success', 'message': 'Acceso concedido'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Usuario o contraseña incorrectos'})
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

def pagina_principal(request):
    usuario = request.session.get('usuario', 'Invitado')  # Obtener el usuario de la sesión
    return render(request, 'pagina_principal.html', {'usuario': usuario})

def get_gerencias(request):
    gerencias = obtener_gerencias()
    return JsonResponse(gerencias, safe=False)

def generar_qr_y_guardar(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        fecha_asignacion = request.POST.get('fecha_asignacion')
        gerencia_id = request.POST.get('gerencia_id')
        
        datos = f"Código de Asignación: {codigo}\nFecha de Asignación: {fecha_asignacion}\nGerencia: {gerencia_id}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(datos)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

        documentos_path = r'C:\Users\JORNADAS1\Documents' 
        qr_dir = os.path.join(documentos_path, 'QR')

        if not os.path.exists(qr_dir): 
            os.makedirs(qr_dir) 
            
        # Generar un nombre de archivo único 
        filename = f"qr_{codigo}_{fecha_asignacion}.png" 
        file_path = os.path.join(qr_dir, filename) 
        
        # Guardar la imagen QR en el archivo 
        with open(file_path, "wb") as f: 
            f.write(buffered.getvalue())

        # Guardar en la base de datos utilizando la función almacenar_asignacion
        exito = almacenar_asignacion(codigo, fecha_asignacion, gerencia_id, buffered.getvalue())
        
        if exito:
            return JsonResponse({'image': img_str, 'file_url': f"{settings.MEDIA_URL}QR/{filename}"})
        else:
            return JsonResponse({'error': 'Error al almacenar la asignación.'}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

def obtener_productos_view(request):
    productos = obtener_productos()
    productos_lista = [
        {
            'id': producto[0],
            'producto': producto[1],
            'marca': producto[2],
            'descripcion': producto[3],
            'color': producto[4],
            'gerencia': producto[5],
            'fecha_registro': producto[6],
        }
        for producto in productos
    ]
    return JsonResponse(productos_lista, safe=False)


def obtener_asignaciones_view(request):
    asignaciones = Consulta_Bienes_Asignados()
    # Añadir un print para verificar los datos
    asignaciones_lista = [
        {
            'id': asignacion[0],
            'codigo': asignacion[1],
            'fecha_asignacion': asignacion[2],
            'gerencia_id': asignacion[3],
            'qr_code': asignacion[4],
        }
        for asignacion in asignaciones
    ]
    return JsonResponse(asignaciones_lista, safe=False)

def generar_informe_view(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        codigo = request.POST.get('codigo')
        fecha_asignacion = request.POST.get('fecha_asignacion')
        gerencia_id = request.POST.get('gerencia_id')

        # Declaraciones de depuración para verificar los valores recibidos
        print(f"ID: {id}")
        print(f"Código: {codigo}")
        print(f"Fecha de Asignación: {fecha_asignacion}")
        print(f"Gerencia ID: {gerencia_id}")

        datos = {
            "{{ID}}": id,
            "{{Codigo}}": codigo,
            "{{FechaAsignacion}}": fecha_asignacion,
            "{{GerenciaID}}": gerencia_id
        }
        print(f"Datos: {datos}")

        qr_code = request.POST.get('qr_code')
        if qr_code:
            print("QR Code recibido:", qr_code)  # Declaración de depuración
            qr_code_parts = qr_code.split(',')
            if len(qr_code_parts) > 1:
                qr_code_base64 = qr_code_parts[1]
                qr_code_data = base64.b64decode(qr_code_base64)
                temp_qr_code_path = os.path.join('C:/Users/JORNADAS1/Documents', 'temp_qr_code.png')
                with open(temp_qr_code_path, 'wb') as temp_file:
                    temp_file.write(qr_code_data)

                ruta_plantilla = os.path.join('C:/Users/JORNADAS1/Documents', 'plantilla.docx')
                nombre_archivo = f'informe_{id}_{codigo}_{fecha_asignacion}_{gerencia_id}.pdf'
                ruta_salida = os.path.join('C:/Users/JORNADAS1/Documents', nombre_archivo)
                
                completar_plantilla(ruta_plantilla, ruta_salida, datos, temp_qr_code_path)

                with open(ruta_salida, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/pdf')
                    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
                    return response
            else:
                print("Error: El formato del QR Code no es el esperado.")
        else:
            print("Error: QR Code no recibido.")
        
    return HttpResponse("Método no permitido", status=405)


def consulta_registros_view(request):
    disponibles = consulta_disponibles()
    # Añadir un print para verificar los datos
    disponibles_lista = [
        {
            'id_Registro': disponibles[0],
            'marca': disponibles[1],
            'producto': disponibles[2],
            'color': disponibles[3],
            'serial': disponibles[4],
            'fecha_registro': disponibles[5],
            'categoria': disponibles[6],
            'cantidad': disponibles[8],
        }
        for disponibles in disponibles
    ]
    return JsonResponse(disponibles_lista, safe=False)