import email
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from paneltrabajador.forms import ProductoForm
from paneltrabajador.models import Producto
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

def producto_listar(request):
    """
    Lista todos los productos si el usuario está autenticado y tiene los permisos necesarios.

    Args:
        request: La solicitud HTTP.

    Returns:
        HttpResponse: La respuesta HTTP que contiene la página de listado de productos o redirige al inicio.
    """
    # El usuario no está autenticado, redireccionar al inicio
    if not request.user.is_authenticated:
        return redirect('panel_home')

    # El usuario no tiene los permisos necesarios, redireccionar al home con un mensaje de error
    if not request.user.has_perm('paneltrabajador.view_producto'):
        messages.error(request, "No tiene los permisos para realizar esto.")
        return redirect('panel_home')

    # Obtenemos todos los objetos del modelo
    productos = Producto.objects.all()
    return render(request, 'paneltrabajador/producto/listado.html', {'productos': productos})

def producto_agregar(request):
    """
    Agrega un nuevo producto si el usuario está autenticado y tiene los permisos necesarios.

    Args:
        request: La solicitud HTTP.

    Returns:
        HttpResponse: La respuesta HTTP que contiene el formulario de producto o redirige al inicio.
    """
    # El usuario no está autenticado, redireccionar al inicio
    if not request.user.is_authenticated:
        return redirect('panel_home')

    # El usuario no tiene los permisos necesarios, redireccionar al home con un mensaje de error
    if not request.user.has_perm('paneltrabajador.add_producto'):
        messages.error(request, "No tiene los permisos para realizar esto.")
        return redirect('panel_home')

    # Se ha enviado el formulario
    if request.method == 'POST':
        # Pasar los datos de la peticion al formulario para la validacion
        form = ProductoForm(request.POST)
        # Todo Ok?
        if form.is_valid():
            # Agregar nuevo objeto
            form.save()
            # Redirige a la página de listado después de agregar un nuevo objeto
            messages.success(request, "Se ha agregado el producto correctamente.")
            return redirect('panel_producto_listar')
    else:
        # Asignar form para mostrarlo en el template
        form = ProductoForm()

    return render(request, 'paneltrabajador/form_generico.html', {'form': form})

def producto_editar(request, id_producto):
    """
    Edita un producto existente si el usuario está autenticado y tiene los permisos necesarios.

    Args:
        request: La solicitud HTTP.
        id_producto: El ID del producto a editar.

    Returns:
        HttpResponse: La respuesta HTTP que contiene el formulario de edición de producto o redirige al inicio.
    """
    # El usuario no está autenticado, redireccionar al inicio
    if not request.user.is_authenticated:
        return redirect('panel_home')

    # El usuario no tiene los permisos necesarios, redireccionar al home con un mensaje de error
    if not request.user.has_perm('paneltrabajador.change_producto'):
        messages.error(request, "No tiene los permisos para realizar esto.")
        return redirect('panel_home')

    # Existe? Entonces asignar. No existe? Entonces mostrar un error 404.
    producto = get_object_or_404(Producto, id_producto=id_producto)

    # Se ha enviado el formulario
    if request.method == 'POST':
        # Pasar los datos de la peticion al formulario para la validacion
        # Aparte le pasamos el objeto para que pueda saber que estamos editando ese objeto en particular
        # En el caso de que no asignaramos instance, pensará que debemos agregar un objeto nuevo
        form = ProductoForm(request.POST, instance=producto)
        # Todo Ok?
        if form.is_valid():
            # Guardar, pero en una variable para poder acceder al objeto inmediatamente abajo
            producto = form.save()

            # Verificamos el stock
            # Si es menor o igual a 0 enviaremos un mensaje al gerente
            if producto.stock_disponible <= 0:
                # Obtener los usuarios con grupo gerente
                usuarios_gerente = get_user_model().objects.filter(groups__name='gerente')
                emails_gerente = []

                # Obtenemos todos los emails y los guardamos
                for usuario in usuarios_gerente:
                    emails_gerente.append(usuario.email)

                # Verificamos si no hay emails
                if len(emails_gerente) == 0:
                    messages.warning(request, "No se han encontrado gerentes para ser notificados.")
                else:
                    # Intentamos enviar el correo
                    try:
                        # Fail_silently=False tirará excepcion
                        # asunto, mensaje, correo, arreglo con destinatarios, Fail_silently
                        send_mail(
                            "AVISO DE STOCK NEGATIVO",
                            "Se ha detectado que el producto {} tiene un stock de {}".format(producto.nombre_producto, producto.stock_disponible),
                            settings.EMAIL_HOST_USER,
                            emails_gerente,
                            fail_silently=False,
                        )
                        messages.info(request, "Se ha notificado el gerente.")

                    # Error!
                    except:
                        messages.error(request, "No se ha podido notificar al gerente. Por favor, comuniquele en persona.")

            return redirect('panel_producto_listar')
    else:
        # Asignar form para mostrarlo en el template
        form = ProductoForm(instance=producto)

    return render(request, 'paneltrabajador/form_generico.html', {'form': form, 'producto': producto})

def producto_eliminar(request, id_producto):
    """
    Elimina un producto si el usuario está autenticado y tiene los permisos necesarios.

    Args:
        request: La solicitud HTTP.
        id_producto: El ID del producto a eliminar.

    Returns:
        HttpResponse: La respuesta HTTP que contiene la confirmación de eliminación o redirige al inicio.
    """
    # El usuario no está autenticado, redireccionar al inicio
    if not request.user.is_authenticated:
        return redirect('panel_home')

    # El usuario no tiene los permisos necesarios, redireccionar al home con un mensaje de error
    if not request.user.has_perm('paneltrabajador.delete_producto'):
        messages.error(request, "No tiene los permisos para realizar esto.")
        return redirect('panel_home')

    # Existe? Entonces asignar. No existe? Entonces mostrar un error 404.
    producto = get_object_or_404(Producto, id_producto=id_producto)

    # El usuario hizo click en OK entonces envio el formulario
    if request.method == 'POST':
        # Eliminar objeto
        producto.delete()
        # Redirige a la página de listado después de eliminar
        messages.success(request, "Se ha eliminado el producto correctamente.")
        return redirect('panel_producto_listar')
    # Asignar contexto para las variables en el template generico
    contexto = {
        'titulo': 'Eliminar Producto',
        'descripcion': '¿Está seguro de que desea eliminar el producto con ID {} y nombre "{}"?'.format(producto.id_producto, producto.nombre_producto),
        'goback': 'panel_producto_listar'
    }

    return render(request, 'paneltrabajador/eliminar_generico.html', contexto)
