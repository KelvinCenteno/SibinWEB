# mi_aplicacion/urls.py
from django.urls import path
from .views import get_gerencias

urlpatterns = [
   path('get_gerencias/', get_gerencias, name='get_gerencias'),
]
