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


    path('panel/usuarios/', vistas_panel.usuario_listar, name='panel_usuario_listar'),
    path('panel/usuarios/agregar/', vistas_panel.usuario_agregar, name='panel_usuario_agregar'),
    path('panel/usuarios/editar/<int:id_usuario>/', vistas_panel.usuario_editar, name='panel_usuario_editar'),
    path('panel/usuarios/eliminar/<int:id_usuario>/', vistas_panel.usuario_eliminar, name='panel_usuario_eliminar'),
    path('panel/usuarios/newpassword/<int:id_usuario>/', vistas_panel.usuario_newpassword, name='panel_usuario_newpassword'),


]
