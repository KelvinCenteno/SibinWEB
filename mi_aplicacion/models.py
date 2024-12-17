from django.db import models

class Usuario(models.Model):
    usuario = models.CharField(max_length=100)
    contrasena = models.CharField(max_length=100)

class Option(models.Model): 
    name = models.CharField(max_length=100) 
    
    def __str__(self): 
        return self.name