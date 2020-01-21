from django.db import models


# Create your models here.

class Producto_ECI(models.Model):
    ean = models.TextField(primary_key=True)
    nombre = models.TextField()
    descripcion = models.TextField()
    link = models.TextField()
    image = models.TextField()

    def __str__(self):
        return self.nombre + ", EAN = " + self.ean


class Historico_ECI(models.Model):
    fecha = models.DateTimeField()
    producto = models.ForeignKey(Producto_ECI, on_delete=models.CASCADE)
    precio = models.TextField()

    def __str__(self):
        return str(self.fecha) + " - Precio: " + self.precio


class Producto_MM(models.Model):
    ean = models.TextField(primary_key=True)
    nombre = models.TextField()
    descripcion = models.TextField()
    link = models.TextField()
    image = models.TextField()

    def __str__(self):
        return self.nombre + ", EAN = " + self.ean


class Historico_MM(models.Model):
    fecha = models.DateTimeField()
    producto = models.ForeignKey(Producto_MM, on_delete=models.CASCADE)
    precio = models.TextField()

    def __str__(self):
        return str(self.fecha) + " - Precio: " + self.precio

class Producto_FC(models.Model):
    ean = models.TextField(primary_key=True)
    nombre = models.TextField()
    descripcion = models.TextField()
    link = models.TextField()
    image = models.TextField()
    
    def __str__(self):
        return self.nombre + ", EAN = " + self.ean
    
class Historico_FC(models.Model):
    fecha = models.DateTimeField()
    producto = models.ForeignKey(Producto_FC, on_delete=models.CASCADE)
    precio = models.TextField()

    def __str__(self):
        return str(self.fecha) + " - Precio: " + self.precio