import json
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .db import *
import qrcode
import segno 
from io import BytesIO
import base64
from django.conf import settings 
import os
from .generar_informe import completar_plantilla
import requests
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
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

            user, created = User.objects.get_or_create(username=usuario, defaults={'password': contrasena}) 
            if created: 
                user.set_unusable_password() 
                user.save() 
            auth_login(request, user)
            request.session['usuario'] = usuario 
            return JsonResponse({'status': 'success', 'message': 'Acceso concedido'}) 
        else:
            return JsonResponse({'status': 'error', 'message': 'Usuario o contraseña incorrectos'})
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

def logout_view(request): 
    logout(request)
    request.session.flush() 
    return redirect('index')

@never_cache
@login_required(login_url='index')
def pagina_principal(request):
    usuario = request.session.get('usuario')  # Obtener el usuario de la sesión
    return render(request, 'pagina_principal.html', {'usuario': usuario})

@never_cache
@login_required(login_url='index')
def administrador(request):
    usuario = request.session.get('usuario')  # Obtener el usuario de la sesión
    return render(request, 'administrador.html', {'usuario': usuario})

def get_gerencias(request):
    gerencias = obtener_gerencias()
    return JsonResponse(gerencias, safe=False)


def generar_qr_y_guardar(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        producto = request.POST.get('producto')
        fecha_asignacion = request.POST.get('fecha_asignacion')
        gerencia_id = request.POST.get('gerencia_id')
        gerencia_name = request.POST.get('gerencia_nombre')

        datos = (
            f"{producto} | "
            f"{codigo} | "
            f"{fecha_asignacion} | "
            f"{gerencia_name}"
        )

        # Crear el código QR con segno y ajustar el tamaño
        qr = segno.make(datos, error='L', micro=False)

        buffered = BytesIO()
        qr.save(buffered, kind='png', scale=5, border=2) 
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

        documentos_path = r'C:\Users\JORNADAS1\Documents'
        qr_dir = os.path.join(documentos_path, 'QR')

        if not os.path.exists(qr_dir):
            os.makedirs(qr_dir)
            
        filename = f"qr_{codigo}_{fecha_asignacion}.png"
        file_path = os.path.join(qr_dir, filename)
        
        with open(file_path, "wb") as f:
            f.write(buffered.getvalue())

        exito = almacenar_asignacion(codigo, fecha_asignacion, gerencia_id, buffered.getvalue())
        
        if exito:
            return JsonResponse({'image': img_str, 'file_url': f"{settings.MEDIA_URL}QR/{filename}"})
        else:
            return JsonResponse({'error': 'Error al almacenar la asignación.'}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)


"""def obtener_productos_view(request):
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
    return JsonResponse(productos_lista, safe=False)"""


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
        datos = {
            "{{ID}}": id,
            "{{Codigo}}": codigo,
            "{{FechaAsignacion}}": fecha_asignacion,
            "{{GerenciaID}}": gerencia_id
        }
        

        qr_code = request.POST.get('qr_code')
        if qr_code:
            qr_code_parts = qr_code.split(',')
            if len(qr_code_parts) > 1:
                qr_code_base64 = qr_code_parts[1]
                qr_code_data = base64.b64decode(qr_code_base64)
                temp_qr_code_path = os.path.join('C:/Users/JORNADAS1/Documents', 'temp_qr_code.png')
                with open(temp_qr_code_path, 'wb') as temp_file:
                    temp_file.write(qr_code_data)

                ruta_plantilla = os.path.join(settings.BASE_DIR, 'templates_word', 'detalles_bienes.docx')
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

def generar_informe_view2(request):
    usuario = request.session.get('usuario') 
    if request.method == 'POST':
        id = request.POST.get('id')
        codigo = request.POST.get('codigo')
        fecha_asignacion = request.POST.get('fecha_asignacion')
        gerencia_id = request.POST.get('gerencia_id')
        qr_code = request.POST.get('qr_code')

        # Obtener datos de la base de datos según el código
        registro = consulta_registro_por_codigo(codigo)
        if not registro:
            return HttpResponse("Registro no encontrado", status=404)

        datos = {
            "{{ID}}": id,
            "{{Codigo}}": codigo,
            "{{FechaAsignacion}}": fecha_asignacion,
            "{{GerenciaID}}": gerencia_id,
            "{{Marca}}": registro[0],
            "{{Producto}}": registro[1],
            "{{Color}}": registro[2],
            "{{Modelo}}": registro[3],
        }

        if qr_code:
            qr_code_parts = qr_code.split(',')
            if len(qr_code_parts) > 1:
                qr_code_base64 = qr_code_parts[1]
                qr_code_data = base64.b64decode(qr_code_base64)
                temp_qr_code_path = os.path.join('C:/Users/JORNADAS1/Documents', 'temp_qr_code.png')
                with open(temp_qr_code_path, 'wb') as temp_file:
                    temp_file.write(qr_code_data)

                ruta_plantilla = os.path.join(settings.BASE_DIR, 'templates_word', 'detalles_bienes3.docx')
                nombre_archivo = f'informe_{id}_{codigo}_{fecha_asignacion}_{gerencia_id}.pdf'
                ruta_salida = os.path.join('C:/Users/JORNADAS1/Documents', nombre_archivo)
                
                completar_plantilla(usuario, ruta_plantilla, ruta_salida, datos, temp_qr_code_path, registro[4])
                
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
    disponibles_lista = [
        {
            'id_Registro': disponibles[0],
            'marca': disponibles[1],
            'producto': disponibles[2],
            'color': disponibles[3],
            'serial': disponibles[4],
            'fecha_registro': disponibles[5],
            'categoria': disponibles[6],
            'foto': disponibles [7],
            'cantidad': disponibles[8],
        }
        for disponibles in disponibles
    ]
    return JsonResponse(disponibles_lista, safe=False)

def consulta_bienes_disponibles(request):
    disponibles = obtener_disponibles()
    disponibles_lista = [
        {
            'id_Registro': disponibles[0],
            'Producto': disponibles[1],
            'Fecha': disponibles[2],
            'categoria': disponibles[3],
            'cantidad': disponibles[5],
        }
        for disponibles in disponibles
    ]
    return JsonResponse(disponibles_lista, safe=False)

def consulta_desincorporacion_view(request):
    desincorporacion = consulta_desincorporacion()
    desincorporacion_lista = [
        {
            'id': desincorporacion[0],
            'codigo_bien': desincorporacion[1],
            'gerencia': desincorporacion[2],
            'fecha_asignacion': desincorporacion[3],
            'motivo_retiro': desincorporacion[4],
            'fecha_retiro': desincorporacion[5],
            'ubicacion_final': desincorporacion[7],
        }
        for desincorporacion in desincorporacion
    ] 
    return JsonResponse(desincorporacion_lista, safe=False)

def get_categorias(request):
    categorias = obtener_categorias()
    return JsonResponse(categorias, safe=False)

def get_marcas(request):
    marcas = obtener_marcas()
    return JsonResponse(marcas, safe=False)

def registrar_bienes(request):
    if request.method == 'POST':
        marca = request.POST.get('marca')
        producto = request.POST.get('producto')
        color = request.POST.get('color')
        serial = request.POST.get('serial')
        fecha_registro = request.POST.get('fecha_registro')
        categoria = request.POST.get('categoria')
        cantidad = request.POST.get('cantidad')

        foto = request.FILES.get('foto')
        if not foto:
            return JsonResponse({'error': 'Foto no proporcionada'}, status=400)

        # Convertir la foto a binario
        foto_binaria = foto.read()

        # Guardar en la base de datos utilizando la función almacenar_registro
        exito = almacenar_registro(marca, producto, color, serial, fecha_registro, categoria, foto_binaria, cantidad)
        
        if exito:
            return JsonResponse({'success': 'Registro almacenado correctamente.'})
        else:
            return JsonResponse({'error': 'Error al almacenar el registro.'}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

def get_bienes(request):
    bienes = obtener_Bienes()
    return JsonResponse(bienes, safe=False)

def get_almacenes(request):
    almacenes = obtener_almacenes()
    return JsonResponse(almacenes, safe=False)

def captura_Desincorporacion(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        codigo = request.POST.get('codigo')
        gerencia = request.POST.get('gerencia')
        fecha = request.POST.get('fecha_asignacion')
        motivo = request.POST.get('motivo')
        ubicacion = request.POST.get('ubicacion_final')
        fecha_actual = datetime.now().strftime("%Y-%m-%d")

        exito = registrar_desincorporacion(id, motivo, fecha_actual, ubicacion)
        if exito:
            return JsonResponse({'success': 'Registro almacenado correctamente.'})
        else:
            return JsonResponse({'error': 'Error al almacenar el registro.'}, status=500)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

def generar_informe_des(request):
    if request.method != 'POST':
        return HttpResponse("Método no permitido", status=405)
    
    usuario = request.session.get('usuario') 
    id = request.POST.get('id')
    codigo = request.POST.get('codigo')

    if not codigo:
        return HttpResponse("Código no puede estar vacío", status=400)
    
    gerencia_id = request.POST.get('gerencia_id')
    fecha_asignacion = request.POST.get('fecha_Asignacion')
    motivo = request.POST.get('motivo')
    fecha_retiro = request.POST.get('fecha_retiro')
    ubicacion = request.POST.get('ubicacion')

    bien = consulta_bien_por_codigo(codigo)

    if bien is None:
        return HttpResponse("Bien no encontrado", status=404)
    
    qr_code = bien[1]
    registro = consulta_registro_por_codigo(bien[0])
    
    if not registro:
        return HttpResponse("Registro no encontrado", status=404)

    datos = {
        "{{ID}}": id,
        "{{Codigo}}": codigo,
        "{{FechaAsignacion}}": fecha_asignacion,
        "{{GerenciaID}}": gerencia_id,
        "{{FechaRetiro}}": fecha_retiro, 
        "{{Motivo}}": motivo,
        "{{Ubicacion}}": ubicacion,
        "{{Marca}}": registro[0],
        "{{Producto}}": registro[1],
        "{{Color}}": registro[2],
        "{{Modelo}}": registro[3],
    }

    if qr_code:
        try:
            qr_code_data = base64.b64decode(qr_code)
            temp_qr_code_path = os.path.join('C:/Users/JORNADAS1/Documents', 'temp_qr_code.png')
            with open(temp_qr_code_path, 'wb') as temp_file:
                temp_file.write(qr_code_data)

            ruta_plantilla = os.path.join(settings.BASE_DIR, 'templates_word', 'detalles_retiro.docx')
            nombre_archivo = f'informe_{id}_{codigo}_{fecha_asignacion}_{gerencia_id}.pdf'
            ruta_salida = os.path.join('C:/Users/JORNADAS1/Documents', nombre_archivo)
            
            completar_plantilla(usuario, ruta_plantilla, ruta_salida, datos, temp_qr_code_path, registro[4])
            
            with open(ruta_salida, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
                return response
        except (base64.binascii.Error, ValueError) as e:
            print(f"Error al decodificar el QR Code: {e}")
            return HttpResponse("Formato de QR Code no válido", status=400)
    else:
        print("Error: QR Code no recibido.")
        return HttpResponse("QR Code no recibido", status=400)

def cambiar_contrasena(request): 
    if request.method == 'POST': 
        datos = json.loads(request.body) 
        usuario = datos.get('usuario') 
        nueva_contrasena = datos.get('nueva_contrasena') 
    
        if not usuario or not nueva_contrasena: 
            return JsonResponse({'success': False, 'message': 'Faltan datos.'}) 
        
        resultado = cambiar_contrasena_bd(usuario, nueva_contrasena) # Usamos la función creada anteriormente 
        
        if resultado: 
            return JsonResponse({'success': True, 'message': 'Cambio exitoso'}) 
        else: 
            return JsonResponse({'success': False, 'message': 'Error al cambiar la contraseña.'}) 

    return JsonResponse({'success': False, 'message': 'Método no permitido.'})
