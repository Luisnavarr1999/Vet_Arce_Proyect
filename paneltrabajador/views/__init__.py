from .home import home, cerrar_sesion
from .cita import cita_agregar, cita_editar, cita_eliminar, cita_listar
from .cliente import cliente_crear, cliente_editar, cliente_eliminar, cliente_listado
from .factura import factura_agregar, factura_editar, factura_eliminar, factura_listar
from .mascota import mascota_agregar, mascota_editar, mascota_eliminar, mascota_listar
from .producto import producto_agregar, producto_editar, producto_eliminar, producto_listar
from .usuarios import usuario_agregar, usuario_editar, usuario_eliminar, usuario_listar, usuario_newpassword

# Este archivo importará todas las vistas en esta carpeta
# Recordar importar aqui en el caso de crear una nueva vista
