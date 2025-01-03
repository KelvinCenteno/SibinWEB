# mi_aplicacion/urls.py
from django.urls import path
from .views import *

urlpatterns = [
   path('get_gerencias/', get_gerencias, name='get_gerencias'),
   path('generar_qr_y_guardar/', generar_qr_y_guardar, name='generar_qr_y_guardar'),
   path('obtener_productos/', obtener_productos_view, name='obtener_productos'),
   path('obtener_asignaciones/', obtener_asignaciones_view, name='obtener_asignaciones'),
   path('generar_informe/', generar_informe_view, name='generar_informe'),
   path('consulta_disponibles/', consulta_registros_view, name='consulta_disponibles'),
   path('consulta_desincorporacion/', consulta_desincorporacion_view, name='consulta_desincorporacion'),
   path('get_categorias/', get_categorias, name='get_categorias'),
   path('get_marcas/', get_marcas, name='get_marcas'),
   path('registrar_bienes/', registrar_bienes, name='registar_bienes'),
   path('get_bienes/', get_bienes, name='get_bienes')
]
