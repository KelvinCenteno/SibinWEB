import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .db import validar_usuario, obtener_gerencias
from .models import Option

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
