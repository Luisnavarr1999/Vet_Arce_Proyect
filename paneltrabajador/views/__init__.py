from .home import home, cerrar_sesion
from .dashboard import dashboard
from .password_reset import password_reset_request, PanelPasswordResetView
from .cita import cita_listar, cita_agregar, cita_editar, cita_eliminar, cita_checkin, cita_noasistio
from .cliente import cliente_crear, cliente_editar, cliente_eliminar, cliente_listado
from .factura import factura_agregar, factura_editar, factura_eliminar, factura_listar
from .mascota import mascota_agregar, mascota_editar, mascota_eliminar, mascota_enviar_recordatorio, mascota_listar, mascota_doc_eliminar
from .producto import producto_agregar, producto_editar, producto_eliminar, producto_listar
from .usuarios import usuario_agregar, usuario_editar, usuario_eliminar, usuario_listar, usuario_newpassword
from .chat import (
    chat_conversation_list,
    chat_conversation_detail,
    chat_conversation_messages,
    chat_pending_count,
)

# Este archivo importará todas las vistas en esta carpeta
# Recordar importar aqui en el caso de crear una nueva vista
