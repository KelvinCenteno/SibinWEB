import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .db import validar_usuario, obtener_gerencias, almacenar_asignacion
#from .models import Option, Asignacion
import qrcode
from io import BytesIO
import base64
from django.conf import settings 
import os

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
