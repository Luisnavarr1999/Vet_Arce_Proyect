from django import forms
from django.utils.safestring import mark_safe
from django.utils.formats import date_format
from django.contrib.auth.forms import PasswordResetForm
from django.utils.timezone import localtime

from paneltrabajador.models import Cita
from .validators import normalize_rut

class ContactForm(forms.Form):
    nombre = forms.CharField(label='Nombre', max_length=150)
    correo = forms.EmailField(label='Correo Electrónico')
    mensaje = forms.CharField(label='Mensaje', widget=forms.Textarea(attrs={'rows': 4}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.setdefault('class', 'form-control')
            field.widget.attrs.setdefault('id', field_name)

class BuscarMascotaForm(forms.Form):
    rut = forms.CharField(label='RUT')
    id_mascota = forms.IntegerField()

    def __init__(self, *args, queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Agrega clases de Bootstrap a los campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    
    def clean_rut(self):
        rut = self.cleaned_data['rut']
        numero, rut_formateado = normalize_rut(rut)
        self.cleaned_data['rut_display'] = rut_formateado
        return numero

class RutForm(forms.Form):
    rut = forms.CharField(label='Ingrese su RUT')

    def __init__(self, *args, queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Agrega clases de Bootstrap a los campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
    
    def clean_rut(self):
        rut = self.cleaned_data['rut']
        numero, rut_formateado = normalize_rut(rut)
        self.cleaned_data['rut_display'] = rut_formateado
        return numero

class MascotaSelectForm(forms.Form):
    mascota = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=mark_safe('Mascota (<a href="?crear_mascota=true">Agregar Nueva</a>)')
    )

    def __init__(self, *args, queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Agrega clases de Bootstrap a los campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        # Permite especificar un queryset (conjunto de consultas) para construir dinámicamente las opciones del campo de selección.
        if queryset is not None:
            self.fields['mascota'].choices = [(m.id_mascota, f"{m.nombre} - {m.especie}") for m in queryset]

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['n_cita']

    def __init__(self, *args, **kwargs):
        servicio = kwargs.pop('servicio', None)
        super().__init__(*args, **kwargs)

        # Agrega clases de Bootstrap a los campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        # Filtra las citas con estado igual a 0 y obtén sus fechas junto al veterinario asignado
        citas_disponibles = Cita.objects.filter(estado='0').select_related('usuario')
        if servicio:
            citas_disponibles = citas_disponibles.filter(servicio=servicio)

        # Crea una lista de tuplas en el formato adecuado para el campo de selección
        opciones = []
        for cita in citas_disponibles:
            fecha_local = localtime(cita.fecha)
            fecha_texto = date_format(fecha_local, 'DATE_FORMAT')
            hora_texto = date_format(fecha_local, 'TIME_FORMAT')
            veterinario = cita.usuario.get_full_name() or cita.usuario.get_username()
            opciones.append(
                (
                    cita.n_cita,
                    f"{fecha_texto} a las {hora_texto} - Veterinario: {veterinario}",
                )
            )

        # Agrega las opciones al campo de selección
        self.fields['n_cita'] = forms.ChoiceField(
            choices=opciones,
            widget=forms.Select(attrs={'class': 'form-control'}),
            label="Seleccione una Fecha y Hora:",
        )

class ServicioForm(forms.Form):
    servicio = forms.ChoiceField(
        choices=Cita.SERVICIO_CHOICES,
        label='Seleccione un servicio',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, available_services=None, **kwargs):
        super().__init__(*args, **kwargs)

        if available_services is not None:
            choices = [
                (value, label)
                for value, label in Cita.SERVICIO_CHOICES
                if value in available_services
            ]
            if choices:
                self.fields['servicio'].choices = choices