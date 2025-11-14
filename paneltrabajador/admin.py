from django.contrib import admin
from paneltrabajador.models import (
    Cita,
    ChatConversation,
    ChatMessage,
    Cliente,
    EvolucionClinica,
    Factura,
    Mascota,
    MascotaDocumento,
    Producto,
    UserProfile,
)

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('n_cita', 'cliente', 'mascota', 'servicio', 'estado', 'asistencia', 'usuario', 'fecha')
    list_filter = ('servicio', 'estado', 'asistencia', 'usuario', 'fecha')
    search_fields = ('cliente__nombre_cliente', 'cliente__rut', 'mascota__nombre', 'usuario__username')
    ordering = ('-fecha',)

class MascotaDocumentoInline(admin.TabularInline):
    model = MascotaDocumento
    extra = 0

class EvolucionClinicaInline(admin.TabularInline):
    model = EvolucionClinica
    extra = 0
    readonly_fields = ('creado_en',)

@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'cliente', 'numero_chip')
    search_fields = ('nombre', 'numero_chip', 'cliente__nombre_cliente', 'cliente__rut')
    inlines = [EvolucionClinicaInline, MascotaDocumentoInline]

admin.site.register(Cliente)
admin.site.register(Producto)
admin.site.register(Factura)
admin.site.register(ChatConversation)
admin.site.register(ChatMessage)
admin.site.register(EvolucionClinica)
admin.site.register(UserProfile)
