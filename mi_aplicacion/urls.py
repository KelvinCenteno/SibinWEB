# mi_aplicacion/urls.py
from django.urls import path
from .views import *
from .db import *

urlpatterns = [
   path('get_gerencias/', get_gerencias, name='get_gerencias'),
   path('generar_qr_y_guardar/', generar_qr_y_guardar, name='generar_qr_y_guardar'),
   #path('obtener_productos/', obtener_productos_view, name='obtener_productos'),
   path('obtener_asignaciones/', obtener_asignaciones_view, name='obtener_asignaciones'),
   path('generar_informe/', generar_informe_view, name='generar_informe'),
   path('generar_informe2/', generar_informe_view2, name='generar_informe2'),
   path('consulta_disponibles/', consulta_registros_view, name='consulta_disponibles'),
   path('consulta_desincorporacion/', consulta_desincorporacion_view, name='consulta_desincorporacion'),
   path('get_categorias/', get_categorias, name='get_categorias'),
   path('get_marcas/', get_marcas, name='get_marcas'),
   path('registrar_bienes/', registrar_bienes, name='registar_bienes'),
   path('get_bienes/', get_bienes, name='get_bienes'),
   path('guardar_excel/', guardar_Bienes_Asignados, name='guardar_excel'),
   path('obtener_disponibles/', consulta_bienes_disponibles, name='obtener_disponibles'),
   path('get_almacenes/', get_almacenes , name='get_almacenes'),
   path('capturar_des/', captura_Desincorporacion , name='capturar_des')
]
