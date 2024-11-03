from django import forms
from django.utils.safestring import mark_safe
from django.utils.formats import date_format

from paneltrabajador.models import Cita

class BuscarMascotaForm(forms.Form):
    rut = forms.IntegerField()
    id_mascota = forms.IntegerField()

    def __init__(self, *args, queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Agrega clases de Bootstrap a los campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class RutForm(forms.Form):
    rut = forms.IntegerField(label='Ingrese su RUT')

    def __init__(self, *args, queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Agrega clases de Bootstrap a los campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

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
        super().__init__(*args, **kwargs)

        # Agrega clases de Bootstrap a los campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        # Filtra las citas con estado igual a 0 y obtén sus fechas e ID
        citas_disponibles = Cita.objects.filter(estado='0').values_list('n_cita', 'fecha')
        # Crea una lista de tuplas en el formato adecuado para el campo de selección
        opciones = [(cita[0], date_format(cita[1], 'DATETIME_FORMAT')) for cita in citas_disponibles]
        # Agrega las opciones al campo de selección
        self.fields['n_cita'] = forms.ChoiceField(choices=opciones, widget=forms.Select(attrs={'class': 'form-control'}), label="Seleccione una Fecha:")
