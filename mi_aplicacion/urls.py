# mi_aplicacion/urls.py
from django.urls import path
from .views import get_gerencias, generar_qr_y_guardar

urlpatterns = [
   path('get_gerencias/', get_gerencias, name='get_gerencias'),
   path('generar_qr_y_guardar/', generar_qr_y_guardar, name='generar_qr_y_guardar'),
]
