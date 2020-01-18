from django.db import models

# Create your models here.

class Producto(models.Model):
    ean = models.TextField(primary_key=True)

    #Media Markt
    nombre_MM = models.TextField()
    descripcion_MM = models.TextField()
    link_MM = models.TextField()

    #El Corte Ingles
    nombre_ECI = models.TextField()
    descripcion_ECI = models.TextField()
    link_ECI = models.TextField()

    def __str__(self):
        return self.nombre_MM + " / " + self.nombre_ECI + ", EAN = " + self.ean

class Historico(models.Model):
    fecha = models.DateTimeField()
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)

    #Media Markt
    precio_MM = models.TextField()

    #El Corte Ingles
    precio_ECI = models.TextField()

    def __str__(self):
        return str(self.fecha) + " - Precio MM: " + self.precio_MM + " / Precio ECI: " + self.precio_ECI