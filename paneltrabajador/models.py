from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
# Create your models here.

class Cliente(models.Model):
    """
    Representa un cliente en el sistema.

    Atributos:
        rut (PositiveIntegerField): ID único del cliente.
        nombre_cliente (CharField): Nombre del cliente.
        direccion (CharField): Dirección del cliente.
        telefono (IntegerField): Número de teléfono del cliente.
        email (EmailField): Dirección de correo electrónico del cliente.
    """
    rut = models.PositiveIntegerField(primary_key=True)
    nombre_cliente = models.CharField(max_length=150)
    direccion = models.CharField(max_length=65)
    telefono = models.IntegerField()
    email = models.EmailField(max_length=254)

    # Devuelve una representación de cadena del objeto Cliente, útil para la visualización en la interfaz de administración de Django.
    # En este caso, también usable en nuestra interfaz personalizada
    def __str__(self):
        """
        Devuelve una representación de cadena del objeto Cliente.
        """
        return f"{self.nombre_cliente} (RUT: {self.rut})"
