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


class Mascota(models.Model):
    """
    Representa una mascota en el sistema.

    Atributos:
        id_mascota (AutoField): ID único de la mascota.
        nombre (CharField): Nombre de la mascota.
        numero_chip (BigIntegerField): Número único del chip de la mascota.
        especie (CharField): Especie de la mascota.
        raza (CharField): Raza de la mascota.
        fecha_nacimiento (DateField): Fecha de nacimiento de la mascota.
        cliente (ForeignKey): Propietario de la mascota (vinculado al modelo Cliente).
        historial_medico (TextField): Historial médico de la mascota.
    """

    id_mascota = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150)
    numero_chip = models.BigIntegerField(unique=True)
    especie = models.CharField(max_length=50)
    raza = models.CharField(max_length=50)
    fecha_nacimiento = models.DateField()
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    historial_medico = models.TextField()

    # Devuelve una representación de cadena del objeto Mascota, útil para la visualización en la interfaz de administración de Django.
    # En este caso, también usable en nuestra interfaz personalizada
    def __str__(self):
        """
        Devuelve una representación de cadena del objeto Mascota.
        """
        return f"{self.nombre} (ID: {self.id_mascota}) de {self.cliente.nombre_cliente} (RUT: {self.cliente.rut})"


class Cita (models.Model):
    """
    Representa una cita en el sistema.

    Atributos:
        n_cita (AutoField): ID único de la cita.
        cliente (ForeignKey): Cliente asociado con la cita (vinculado al modelo Cliente).
        mascota (ForeignKey): Mascota asociada con la cita (vinculada al modelo Mascota).
        estado (CharField): Estado de la cita.
        usuario (ForeignKey): Usuario que creó la cita (vinculado al modelo User).
        fecha (DateTimeField): Fecha y hora de la cita.
    """

    # Definimos las opciones que puede tener el estado de la Cita
    # Nota: verificar si podemos transformar esto a una tupla en vez de un arreglo
    ESTADO_CHOICES = [
        ('0', 'Disponible'),
        ('1', 'Reservada'),
        ('2', 'Cancelada'),
    ]

    n_cita = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True)
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, null=True)
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES)
    usuario = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    fecha = models.DateTimeField()

    # Obtenemos el estado pero transformado para el objeto actual
    # Es decir, si self.estado es = 0 entonces se mostrará "Disponible"
    def get_estado_display(self):
        """
        Devuelve el valor de visualización para el campo 'estado'.
        """
        return self.ESTADO_CHOICES[int(self.estado)][1]

    # Obtener el listado de citas
    # Se hizo esta función para que el listado salga con todos los estados transformados por defecto
    def get_for_listado(**args):
        """
        Devuelve una lista de citas con valores de estado transformados.

        Args:
            **args: Argumentos adicionales de consulta.

        Returns:
            queryset: Un queryset de citas.
        """

        listado = Cita.objects.filter(**args)

        # Mostramos el estado que corresponde
        for cita in listado:
            cita.estado = cita.get_estado_display()
        return listado


class Producto (models.Model):
    """
    Representa un producto en el sistema.

    Atributos:
        id_producto (AutoField): ID único del producto.
        nombre_producto (CharField): Nombre del producto.
        stock_disponible (IntegerField): Stock disponible del producto.
    """
    id_producto = models.AutoField(primary_key=True)
    nombre_producto = models.CharField(max_length=30)
    stock_disponible = models.IntegerField()


class Factura(models.Model):
    """
    Representa una factura en el sistema.

    Atributos:
        numero_factura (AutoField): ID único de la factura.
        cliente (ForeignKey): Cliente asociado con la factura (vinculado al modelo Cliente).
        total_pagar (IntegerField): Monto total a pagar.
        detalle (TextField): Detalles de la factura.
        estado_pago (CharField): Estado de pago de la factura.
    """
    numero_factura = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    total_pagar = models.IntegerField()
    detalle = models.TextField()
    estado_pago = models.CharField(max_length=1)
