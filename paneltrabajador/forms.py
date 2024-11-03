from django import forms
from .models import Cita, Cliente, Mascota, Factura, Producto
from django.contrib.auth import get_user_model

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
        fields = ['cliente', 'mascota', 'estado', 'usuario', 'fecha']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Agrega clases de Bootstrap a los campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        self.fields['fecha'] = DateTimeLocalField()

        self.fields['estado'].widget.attrs['class'] = 'form-select'
        self.fields['cliente'].widget.attrs['class'] = 'form-select'
        self.fields['usuario'].widget.attrs['class'] = 'form-select'
        self.fields['mascota'].widget.attrs['class'] = 'form-select'

        self.fields['cliente'].required = False
        self.fields['mascota'].required = False

        # Ocultamos los campos "cliente" y "mascota" si estamos agregando una nueva cita
        if not self.instance.pk:  # Verificamos si la instancia ya tiene una clave primaria
            self.fields['cliente'].widget = forms.HiddenInput()
            self.fields['mascota'].widget = forms.HiddenInput()


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

        # Agrega clases de Bootstrap a los campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        self.fields['cliente'].widget.attrs['class'] = 'form-select'

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
            if field_name is not 'is_active':
                field.widget.attrs['class'] = 'form-control'
