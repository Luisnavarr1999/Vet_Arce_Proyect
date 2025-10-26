from django.contrib import admin

from paneltrabajador.models import Cita, Cliente, Factura, Mascota, Producto

# Registramos los modelos para poder visualizarlos en Django ADMIN

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('n_cita', 'cliente', 'mascota', 'estado', 'asistencia', 'usuario', 'fecha')
    list_filter = ('estado', 'asistencia', 'usuario', 'fecha')
    search_fields = ('cliente__nombre_cliente', 'cliente__rut', 'mascota__nombre', 'usuario__username')
    ordering = ('-fecha',)

admin.site.register(Cliente)
admin.site.register(Mascota)
admin.site.register(Producto)
admin.site.register(Factura)
