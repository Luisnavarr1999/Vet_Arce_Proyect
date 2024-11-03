"""
URL configuration for ficatsmanager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from ambpublica import views as vistas_publica
from paneltrabajador import views as vistas_panel

urlpatterns = [
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),

    path('panel/', vistas_panel.home, name="panel_home"),
    path('panel/logout/', vistas_panel.cerrar_sesion, name="panel_logout"),

    path('panel/clientes/', vistas_panel.cliente_listado, name="panel_cliente_listado"),
    path('panel/clientes/nuevo/', vistas_panel.cliente_crear, name="panel_cliente_nuevo"),
    path('panel/clientes/editar/<int:rut>/', vistas_panel.cliente_editar, name='panel_cliente_editar'),
    path('panel/clientes/eliminar/<int:rut>/', vistas_panel.cliente_eliminar, name='panel_cliente_eliminar'),

    path('panel/citas/', vistas_panel.cita_listar, name="panel_cita_listar"),
    path('panel/citas/nuevo/', vistas_panel.cita_agregar, name="panel_cita_nuevo"),
    path('panel/citas/editar/<int:n_cita>/', vistas_panel.cita_editar, name='panel_cita_editar'),
    path('panel/citas/eliminar/<int:n_cita>/', vistas_panel.cita_eliminar, name='panel_cita_eliminar'),

    path('panel/mascotas/', vistas_panel.mascota_listar, name='panel_mascota_listar'),
    path('panel/mascotas/nuevo/', vistas_panel.mascota_agregar, name='panel_mascota_nuevo'),
    path('panel/mascotas/editar/<int:id_mascota>/', vistas_panel.mascota_editar, name='panel_mascota_editar'),
    path('panel/mascotas/eliminar/<int:id_mascota>/', vistas_panel.mascota_eliminar, name='panel_mascota_eliminar'),

    path('panel/facturas/', vistas_panel.factura_listar, name='panel_factura_listar'),
    path('panel/facturas/nuevo/', vistas_panel.factura_agregar, name='panel_factura_nuevo'),
    path('panel/facturas/editar/<int:numero_factura>/', vistas_panel.factura_editar, name='panel_factura_editar'),
    path('panel/facturas/eliminar/<int:numero_factura>/', vistas_panel.factura_eliminar, name='panel_factura_eliminar'),

    path('panel/productos/', vistas_panel.producto_listar, name='panel_producto_listar'),
    path('panel/productos/agregar/', vistas_panel.producto_agregar, name='panel_producto_agregar'),
    path('panel/productos/editar/<int:id_producto>/', vistas_panel.producto_editar, name='panel_producto_editar'),
    path('panel/productos/eliminar/<int:id_producto>/', vistas_panel.producto_eliminar, name='panel_producto_eliminar'),

    path('panel/usuarios/', vistas_panel.usuario_listar, name='panel_usuario_listar'),
    path('panel/usuarios/agregar/', vistas_panel.usuario_agregar, name='panel_usuario_agregar'),
    path('panel/usuarios/editar/<int:id_usuario>/', vistas_panel.usuario_editar, name='panel_usuario_editar'),
    path('panel/usuarios/eliminar/<int:id_usuario>/', vistas_panel.usuario_eliminar, name='panel_usuario_eliminar'),
    path('panel/usuarios/newpassword/<int:id_usuario>/', vistas_panel.usuario_newpassword, name='panel_usuario_newpassword'),

    path('', vistas_publica.main, name="ambpublico_index"),
    path('consulta_mascota/', vistas_publica.consulta_mascota, name="ambpublico_consulta"),
    path('reservahora/', vistas_publica.reserva_hora, name="ambpublico_reserva"),
    path('reservahora/cancelar/', vistas_publica.reserva_hora_cancelar, name="ambpublico_reserva_cancelar"),
]
