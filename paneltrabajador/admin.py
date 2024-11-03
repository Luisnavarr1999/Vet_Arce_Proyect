from django.contrib import admin

from paneltrabajador.models import Cita, Cliente, Factura, Mascota, Producto

# Registramos los modelos para poder visualizarlos en Django ADMIN
admin.site.register(Cliente)
admin.site.register(Mascota)
admin.site.register(Producto)
admin.site.register(Factura)
admin.site.register(Cita)
