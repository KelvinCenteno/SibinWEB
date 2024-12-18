from django.db import models

class Usuario(models.Model):
    usuario = models.CharField(max_length=100)
    contrasena = models.CharField(max_length=100)

class Option(models.Model): 
    name = models.CharField(max_length=100) 
    
    def __str__(self): 
        return self.name
    
class Asignacion(models.Model):
    codigo = models.CharField(max_length=100)
    fecha_asignacion = models.DateField()
    gerencia_id = models.IntegerField()
    qr_code = models.BinaryField()  # Para almacenar la imagen del QR

    def __str__(self):
        return f"{self.codigo} - {self.fecha_asignacion} - {self.gerencia_id}"
