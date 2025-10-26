from django import forms
from .models import Cita, Cliente, Mascota, Factura, Producto
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm 
from django.contrib.auth.forms import SetPasswordForm
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from django.forms.widgets import DateTimeInput
from django.core.exceptions import ValidationError
from django.utils import timezone

# https://stackoverflow.com/a/69965027
class DateTimeLocalInput(forms.DateTimeInput):
    input_type = "datetime-local"


class DateTimeLocalField(forms.DateTimeField):
    # Set DATETIME_INPUT_FORMATS here because, if USE_L10N
    # is True, the locale-dictated format will be applied
    # instead of settings.DATETIME_INPUT_FORMATS.
    # See also:
    # https://developer.mozilla.org/en-US/docs/Web/HTML/Date_and_time_formats

    input_formats = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M"
    ]
    widget = DateTimeLocalInput(format="%Y-%m-%dT%H:%M", attrs={'class': 'form-control'})


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['rut', 'nombre_cliente', 'direccion', 'telefono', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Agrega clases de Bootstrap a los campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        # Deshabilitar la edición del campo 'rut' si ya existe el cliente
        # se asegura de que el formulario esté en modo de edición y no en modo de creación.
        if self.instance and self.instance.pk:
            self.fields['rut'].widget = forms.HiddenInput()


class CitaForm(forms.ModelForm):
    
    class Meta:
        model = Cita
        fields = ['cliente', 'mascota', 'estado', 'usuario', 'fecha', 'asistencia']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'usuario': forms.Select(attrs={'class': 'form-select'}),
            'mascota': forms.Select(attrs={'class': 'form-select'}),
            'asistencia': forms.Select(attrs={'class': 'form-select'}),
        }
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

         # Bootstrap para todos los campos (por si algún widget no es select)
        for _, field in self.fields.items():
            field.widget.attrs.setdefault('class', 'form-control')

         # Input de fecha/hora local (usa tu DateTimeLocalField definido arriba)
        self.fields['fecha'] = DateTimeLocalField()

        # Reglas de requerido
        self.fields['cliente'].required = False
        self.fields['mascota'].required = False

         # Ocultar cliente/mascota al crear (como ya hacías)
        if not (self.instance and self.instance.pk):
            self.fields['cliente'].widget = forms.HiddenInput()
            self.fields['mascota'].widget = forms.HiddenInput()
        else:
            # Valor inicial cuando EDITAS: respeta lo que tenga el modelo (default 'P')
            self.fields['asistencia'].initial = self.instance.asistencia or 'P'
        
    def clean(self):
        cleaned = super().clean()
        estado = cleaned.get('estado')            # '0','1','2'
        fecha = cleaned.get('fecha')
        asistencia = cleaned.get('asistencia')    # 'P','A','N'
        now = timezone.now()

        # Solo permite A/N si estaba RESERVADA y ya ocurrió
        if asistencia in ('A', 'N'):
            if estado != '1' or (fecha and fecha > now):
                raise ValidationError(
                    "Solo puedes marcar 'Asistió' o 'No asistió' cuando la cita fue 'Reservada' y ya ocurrió."
                )
        return cleaned

ESPECIE_CHOICES = [
    ("Perro", "Perro"),
    ("Gato", "Gato"),
    ("Otros", "Otros"),
]


RAZA_OPTIONS = {
    "Perro": [
        "Mestizo",
        "Labrador Retriever",
        "Pastor Alemán",
        "Poodle",
        "Bulldog",
        "Beagle",
        "Golden Retriever",
        "Chihuahua",
        "Pug",
        "Schnauzer",
    ],
    "Gato": [
        "Mestizo",
        "Siamés",
        "Persa",
        "Maine Coon",
        "Bengalí",
        "Sphynx",
        "British Shorthair",
        "Abisinio",
        "Angora Turco",
        "Ragdoll",
    ],
    "Otros": [
        "Erizo",
        "Hámster",
        "Ratón",
        "Cobaya",
        "Conejo",
        "Hurón",
        "Tortuga",
        "Iguana",
        "Ave Exótica",
        "Pez",
    ],
}


def _flatten_raza_choices():
    """Genera las tuplas (valor, etiqueta) para todas las razas disponibles."""

    flattened = []
    for razas in RAZA_OPTIONS.values():
        for raza in razas:
            choice = (raza, raza)
            if choice not in flattened:
                flattened.append(choice)
    return flattened


class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = ['nombre', 'numero_chip', 'especie', 'raza', 'fecha_nacimiento', 'cliente', 'historial_medico']
        widgets = {
            'fecha_nacimiento': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'placeholder': 'Seleccione una fecha...', 'type': 'date'}),
        }

    def __init__(self, *args, es_reserva=False, **kwargs):
        super().__init__(*args, **kwargs)

        raza_choices = _flatten_raza_choices()

        # Configura el selector de especie
        self.fields['especie'].widget = forms.Select(choices=ESPECIE_CHOICES)
        self.fields['especie'].choices = ESPECIE_CHOICES

        # Configura el selector de raza
        self.fields['raza'].widget = forms.Select(choices=raza_choices)
        self.fields['raza'].choices = raza_choices

        # Agrega clases de Bootstrap a los campos
        for field_name, field in self.fields.items():
            if field_name in ('especie', 'raza', 'cliente'):
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'

        # Asegura que la raza actual esté presente en la lista de opciones (edición)
        if self.instance and self.instance.pk:
            raza_actual = self.instance.raza
            if raza_actual and (raza_actual, raza_actual) not in self.fields['raza'].choices:
                self.fields['raza'].choices = list(self.fields['raza'].choices) + [(raza_actual, raza_actual)]
                
        if es_reserva == True:
            self.fields.pop('cliente')
            self.fields.pop('historial_medico')


class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = ['cliente', 'total_pagar', 'detalle', 'estado_pago']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Agrega clases de Bootstrap a los campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        self.fields['cliente'].widget.attrs['class'] = 'form-select'


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre_producto', 'stock_disponible']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Agrega clases de Bootstrap a los campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class UsuarioForm(forms.ModelForm):

    # Constante de tuplas con las opciones que tiene el selector de los roles de usuario
    ROL_CHOICES = (
        ('veterinario', 'Veterinario'),
        ('gerente', 'Gerente'),
        ('recepcionista', 'Recepcionista'),
    )

    # Asignamos nuestro campo personalizado con las opciones y siendo obligatorio
    rol_usuario = forms.ChoiceField(choices=ROL_CHOICES, required=True)

    class Meta:
        # El modelo lo obtenemos desde la autentificacion de Django
        model = get_user_model()

        # Is_Active sirve para no tener que eliminar el usuario, solamente dejarlo sin poder acceder
        fields = ['first_name', 'last_name', 'username', 'email', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Verificamos si la instancia ya tiene una clave primaria, es decir, estamos editando un usuario
        if self.instance.pk:
            # Si estamos editando un usuario, entonces vamos a obtener su grupo de usuario desde Django Auth
            # Y lo vamos a asignar el select de rol_usuario
            if self.instance.groups.filter(name='veterinario').exists():
                self.fields['rol_usuario'].initial = "veterinario"
            if self.instance.groups.filter(name='gerente').exists():
                self.fields['rol_usuario'].initial = "gerente"
            if self.instance.groups.filter(name='recepcionista').exists():
                self.fields['rol_usuario'].initial = "recepcionista"

        # Agrega clases de Bootstrap a los campos
        for field_name, field in self.fields.items():
            if field_name != 'is_active':
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-check-input'

class PasswordResetRequestForm(PasswordResetForm):
    """Valida que el correo exista y envía el mail con HTML + Reply-To."""

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not list(self.get_users(email)):
            raise forms.ValidationError(
                "No existe un usuario registrado con ese correo electrónico.",
                code="email_not_found",
            )
        return email

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        # subject sin saltos de línea
        subject = render_to_string(subject_template_name, context).strip()

        # texto plano
        body_text = render_to_string(email_template_name, context)

        # Construye el mensaje
        msg = EmailMultiAlternatives(
            subject=subject,
            body=body_text,
            from_email=from_email,
            to=[to_email],
            headers=({"Reply-To": context.get("reply_to")} if context.get("reply_to") else None),
        )

        # HTML
        if html_email_template_name:
            body_html = render_to_string(html_email_template_name, context)
            msg.attach_alternative(body_html, "text/html")

        msg.send()
    
class StyledSetPasswordForm(SetPasswordForm):
    """Agrega clases Bootstrap a los campos del formulario de nueva contraseña."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            # clase Bootstrap
            field.widget.attrs.setdefault("class", "form-control")
            # autocompletado recomendado por Django para nuevos passwords
            field.widget.attrs.setdefault("autocomplete", "new-password")
            # placeholders opcionales
            if name == "new_password1":
                field.widget.attrs.setdefault("placeholder", "Nueva contraseña")
            elif name == "new_password2":
                field.widget.attrs.setdefault("placeholder", "Confirmar contraseña")

