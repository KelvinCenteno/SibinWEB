# mi_aplicacion/urls.py
from django.urls import path
from .views import get_gerencias, generar_qr_y_guardar, obtener_productos_view, obtener_asignaciones_view, generar_informe_view

urlpatterns = [
   path('get_gerencias/', get_gerencias, name='get_gerencias'),
   path('generar_qr_y_guardar/', generar_qr_y_guardar, name='generar_qr_y_guardar'),
   path('obtener_productos/', obtener_productos_view, name='obtener_productos'),
   path('obtener_asignaciones/', obtener_asignaciones_view, name='obtener_asignaciones'),
   path('generar_informe/', generar_informe_view, name='generar_informe'),
]
