from django.db import models

class Usuario(models.Model):
    usuario = models.CharField(max_length=100)
    contrasena = models.CharField(max_length=100)
