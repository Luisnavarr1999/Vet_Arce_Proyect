from django import forms
from django.utils.safestring import mark_safe
from django.utils.formats import date_format

from paneltrabajador.models import Cita



class RutForm(forms.Form):
    rut = forms.IntegerField(label='Ingrese su RUT')

    def __init__(self, *args, queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Agrega clases de Bootstrap a los campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


    def __init__(self, *args, queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Agrega clases de Bootstrap a los campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        # Permite especificar un queryset (conjunto de consultas) para construir dinámicamente las opciones del campo de selección.
        if queryset is not None:
            self.fields['mascota'].choices = [(m.id_mascota, f"{m.nombre} - {m.especie}") for m in queryset]
