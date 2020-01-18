from django.db import models

# Create your models here.
class Producto(models.Model):
    ean = models.TextField(primary_key=True)

    #Media Markt
    nombre_MM = models.TextField()
    precio_MM = models.TextField()
    link_MM = models.TextField()

    #El Corte Ingles
    nombre_ECI = models.TextField()
    precio_ECI = models.TextField()
    link_ECI = models.TextField()


    def __str__(self):
        return self.nombre_MM " / " + self.nombre_ECI + ", EAN= " + self.ean