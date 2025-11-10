import os
from typing import Optional
from django.db import models
from django.db import OperationalError, ProgrammingError
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
from django.utils import timezone

# Create your models here.

class Cliente(models.Model):
    """
    Representa un cliente en el sistema.

    Atributos:
        rut (PositiveIntegerField): ID único del cliente.
        nombre_cliente (CharField): Nombre del cliente.
        direccion (CharField): Dirección del cliente.
        telefono (CharField): Número de teléfono del cliente en formato +56XXXXXXXXX.
        email (EmailField): Dirección de correo electrónico del cliente.
    """
    rut = models.PositiveIntegerField(primary_key=True)
    nombre_cliente = models.CharField(max_length=150)
    direccion = models.CharField(max_length=65)
    telefono = models.CharField(
        max_length=12,
        validators=[
            RegexValidator(
                regex=r"^\+56\d{9}$",
                message="El teléfono debe tener el formato +56 seguido de 9 dígitos.",
            )
        ],
    )
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
    historial_medico = models.TextField(blank=True, default="")

    # Devuelve una representación de cadena del objeto Mascota, útil para la visualización en la interfaz de administración de Django.
    # En este caso, también usable en nuestra interfaz personalizada
    def __str__(self):
        """
        Devuelve una representación de cadena del objeto Mascota.
        """
        return f"{self.nombre} (ID: {self.id_mascota}) de {self.cliente.nombre_cliente} (RUT: {self.cliente.rut})"

class MascotaDocumento(models.Model):
    """Documento asociado al historial clínico de una mascota."""

    mascota = models.ForeignKey(
        Mascota,
        on_delete=models.CASCADE,
        related_name='documentos',
    )
    evolucion = models.ForeignKey(
        'EvolucionClinica',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='documentos',
    )
    archivo = models.FileField(upload_to='mascotas/documentos/')
    subido_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-subido_en']

    def __str__(self):
        return self.nombre_archivo

    @property
    def nombre_archivo(self) -> str:
        return os.path.basename(self.archivo.name)
    
    def delete(self, using=None, keep_parents=False):
        """
        Borra primero el registro y luego elimina el archivo del storage si existe.
        """
        storage = self.archivo.storage
        name = self.archivo.name
        super().delete(using=using, keep_parents=keep_parents)
        if name and storage.exists(name):
            storage.delete(name)


class CitaQuerySet(models.QuerySet):
    """QuerySet personalizado para refrescar citas disponibles expiradas."""

    def actualizar_no_tomadas(self):
        now = timezone.now()
        self.filter(estado='0', fecha__lt=now).update(estado='3', asistencia=None)
        return self


class CitaManager(models.Manager.from_queryset(CitaQuerySet)):
    """Manager que marca automáticamente las citas vencidas como no tomadas."""

    def get_queryset(self):
        qs = super().get_queryset()
        try:
            qs.filter(estado='0', fecha__lt=timezone.now()).update(estado='3', asistencia=None)
        except (OperationalError, ProgrammingError):
            # La base de datos no está disponible (por ejemplo en migraciones iniciales).
            pass
        return qs

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
        ('3', 'No tomada'),
    ]

    ASISTENCIA_CHOICES = [
        ('P', 'Pendiente'),
        ('A', 'Asistió'),
        ('N', 'No asistió'),
    ]

    SERVICIO_CHOICES = [
        ('general', 'Consulta General'),
        ('cirugia', 'Cirugía'),
        ('dentista', 'Dentista'),
    ]
    
    n_cita = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True)
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, null=True)
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES)
    usuario = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    fecha = models.DateTimeField()
    asistencia = models.CharField(
        max_length=1,
        choices=ASISTENCIA_CHOICES,
        default='P',
        null=True,
        blank=True,
    )
    servicio = models.CharField(max_length=20, choices=SERVICIO_CHOICES, default='general')

     # Auditoría del check-in (sirve para registrar automáticamente quién y cuándo marcó la asistencia)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    checked_in_by = models.ForeignKey(
        get_user_model(), null=True, blank=True,
        on_delete=models.SET_NULL, related_name='checkins'
    )

    objects = CitaManager()

    @property
    def puede_confirmar_asistencia(self):
        # solo si está reservada y la hora ya llegó o pasó
        return self.estado == '1' and self.fecha <= timezone.now()

    @property
    def asistio(self):
        return self.asistencia == 'A'

    @property
    def no_asistio(self):
        return self.asistencia == 'N'

    @staticmethod
    def get_for_listado(**args):
        return Cita.objects.filter(**args).order_by('-fecha')
    
    def save(self, *args, **kwargs):
        update_fields = kwargs.get('update_fields')
        if update_fields is not None:
            update_fields = set(update_fields)

        if self.estado in ('2', '3'):
            self.asistencia = None
            if update_fields is not None:
                update_fields.add('asistencia')
        elif self.estado == '1' and self.asistencia is None:
            self.asistencia = 'P'
            if update_fields is not None:
                update_fields.add('asistencia')

        if update_fields is not None:
            kwargs['update_fields'] = update_fields

        super().save(*args, **kwargs)


class EvolucionClinica(models.Model):
    """Entrada cronológica que describe una atención o seguimiento de la mascota."""

    mascota = models.ForeignKey(
        Mascota,
        on_delete=models.CASCADE,
        related_name='evoluciones',
    )
    cita = models.ForeignKey(
        'Cita',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evoluciones',
    )
    servicio = models.CharField(max_length=20, choices=Cita.SERVICIO_CHOICES, default='general')
    resumen = models.CharField(max_length=255)
    detalle = models.TextField()
    recomendaciones = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado_en']

    def __str__(self):
        return f"Evolución de {self.mascota.nombre} ({self.get_servicio_display()})"

    @property
    def fecha_evento(self):
        """Devuelve la fecha relevante para mostrar en la ficha pública."""

        if self.cita and self.cita.fecha:
            return self.cita.fecha
        return self.creado_en

    def save(self, *args, **kwargs):
        if self.cita and not self.servicio:
            self.servicio = self.cita.servicio
        super().save(*args, **kwargs)


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

class ChatConversation(models.Model):
    """Conversación iniciada desde el chatbot público."""

    STATE_PENDING = "pending"
    STATE_ACTIVE = "active"
    STATE_CLOSED = "closed"
    STATE_CHOICES = [
        (STATE_PENDING, "Pendiente"),
        (STATE_ACTIVE, "Activa"),
        (STATE_CLOSED, "Cerrada"),
    ]

    source = models.CharField(max_length=30, default="web")
    initial_question = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="chat_conversations",
    )
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default=STATE_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message_at = models.DateTimeField(auto_now_add=True)
    last_message_preview = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-last_message_at"]
        verbose_name = "Conversación de Chat"
        verbose_name_plural = "Conversaciones de Chat"

    def __str__(self):
        return f"Conversación #{self.pk} ({self.get_state_display()})"

    def touch(self, summary: Optional[str] = None):
        now = timezone.now()
        self.last_message_at = now
        if summary is not None:
            self.last_message_preview = summary[:255]
        self.save(update_fields=["last_message_at", "last_message_preview", "updated_at"])


class ChatMessage(models.Model):
    """Mensaje dentro de una conversación del chat."""

    AUTHOR_BOT = "bot"
    AUTHOR_CLIENT = "client"
    AUTHOR_STAFF = "staff"
    AUTHOR_CHOICES = [
        (AUTHOR_BOT, "Bot"),
        (AUTHOR_CLIENT, "Cliente"),
        (AUTHOR_STAFF, "Recepcionista"),
    ]

    conversation = models.ForeignKey(
        ChatConversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    author = models.CharField(max_length=20, choices=AUTHOR_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    staff_user = models.ForeignKey(
        get_user_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="chat_messages",
    )

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Mensaje de Chat"
        verbose_name_plural = "Mensajes de Chat"

    def __str__(self):
        return f"Mensaje de {self.get_author_display()} en conversación #{self.conversation_id}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.conversation.touch(summary=self.content)
