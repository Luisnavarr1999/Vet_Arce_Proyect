from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from paneltrabajador.forms import ClienteForm
from paneltrabajador.models import Cliente, Mascota
def cliente_listado(request):
    """
    Vista para listar todos los clientes.

    Requiere que el usuario esté autenticado y tenga permisos para ver clientes.

    :param request: Objeto HttpRequest.
    :return: HttpResponse con la lista de clientes.
    """
    # El usuario no está autenticado, redireccionar al inicio
    if not request.user.is_authenticated:
        return redirect('panel_home')

    # El usuario no tiene los permisos necesarios, redireccionar al home con un mensaje de error
    if not request.user.has_perm('paneltrabajador.view_cliente'):
        messages.error(request, "No tiene los permisos para realizar esto.")
        return redirect('panel_home')

    # Obtenemos todos los objetos del modelo
    clientes = Cliente.objects.all()
    return render(request, 'paneltrabajador/cliente/listado.html', {'clientes': clientes})


def cliente_crear(request):
    """
    Vista para agregar un nuevo cliente.

    Requiere que el usuario esté autenticado y tenga permisos para agregar clientes.

    :param request: Objeto HttpRequest.
    :return: HttpResponse con el formulario de agregar cliente.
    """
    # El usuario no está autenticado, redireccionar al inicio
    if not request.user.is_authenticated:
        return redirect('panel_home')

    # El usuario no tiene los permisos necesarios, redireccionar al home con un mensaje de error
    if not request.user.has_perm('paneltrabajador.add_cliente'):
        messages.error(request, "No tiene los permisos para realizar esto.")
        return redirect('panel_home')

    # Se ha enviado el formulario
    if request.method == 'POST':
        # Pasar los datos de la peticion al formulario para la validacion
        form = ClienteForm(request.POST)
        # Todo Ok?
        if form.is_valid():
            # Agregar nuevo objeto
            form.save()
            # Redirige a la página de listado después de agregar un nuevo objeto
            messages.success(request, "Se ha creado el cliente correctamente.")
            return redirect('panel_cliente_listado')
    else:
        # Asignar form para mostrarlo en el template
        form = ClienteForm()

    return render(request, 'paneltrabajador/form_generico.html', {'form': form})


def cliente_editar(request, rut):
    """
    Vista para editar un cliente existente.

    Requiere que el usuario esté autenticado y tenga permisos para editar clientes.

    :param request: Objeto HttpRequest.
    :param rut: Rut del cliente a editar.
    :return: HttpResponse con el formulario de editar cliente.
    """
    # El usuario no está autenticado, redireccionar al inicio
    if not request.user.is_authenticated:
        return redirect('panel_home')

    # El usuario no tiene los permisos necesarios, redireccionar al home con un mensaje de error
    if not request.user.has_perm('paneltrabajador.change_cliente'):
        messages.error(request, "No tiene los permisos para realizar esto.")
        return redirect('panel_home')

    # Obtener el objeto Cliente según su rut o devuelve una página 404 si no existe.
    cliente = get_object_or_404(Cliente, rut=rut)

    # Se ha enviado el formulario
    if request.method == 'POST':
        # Pasar los datos de la peticion al formulario para la validacion
        # Aparte le pasamos el objeto para que pueda saber que estamos editando ese objeto en particular
        # En el caso de que no asignaramos instance, pensará que debemos agregar un objeto nuevo
        form = ClienteForm(request.POST, instance=cliente)
        # Todo Ok?
        if form.is_valid():
            # Guardar
            form.save()
            # Redirige a la página de listado después de editar
            messages.success(
                request, "Se ha editado el cliente correctamente.")
            return redirect('panel_cliente_listado')
    else:
        # Asignar form para mostrarlo en el template
        form = ClienteForm(instance=cliente)

    # Necesario para mostrar las mascotas
    mascotas = Mascota.objects.filter(cliente=cliente)

    # Renderizamos el formulario de cliente, no el generico
    return render(request, 'paneltrabajador/cliente/form.html', {'form': form, 'cliente': cliente, 'mascotas': mascotas})


def cliente_eliminar(request, rut):
    """
    Vista para eliminar un cliente existente.

    Requiere que el usuario esté autenticado y tenga permisos para eliminar clientes.

    :param request: Objeto HttpRequest.
    :param rut: Rut del cliente a eliminar.
    :return: HttpResponse con el formulario de confirmación de eliminación.
    """
    # El usuario no está autenticado, redireccionar al inicio
    if not request.user.is_authenticated:
        return redirect('panel_home')

    # El usuario no tiene los permisos necesarios, redireccionar al home con un mensaje de error
    if not request.user.has_perm('paneltrabajador.delete_cliente'):
        messages.error(request, "No tiene los permisos para realizar esto.")
        return redirect('panel_home')

    # Obtener el objeto Cliente según su rut o devuelve una página 404 si no existe.
    cliente = get_object_or_404(Cliente, rut=rut)

    # El usuario hizo click en OK entonces envio el formulario
    if request.method == 'POST':
        # Eliminar objeto
        cliente.delete()
        messages.success(request, "Se ha eliminado el cliente correctamente.")
        # Redirige a la página de listado después de eliminar
        return redirect('panel_cliente_listado')

    # Asignar contexto para las variables en el template generico
    contexto = {
        'titulo': 'Eliminar Cliente',
        'descripcion': '¿Está seguro que desea eliminar al cliente con RUT {}? Recuerde que sus mascotas y toda información relacionada será eliminada de igual manera. '.format(cliente.nombre_cliente),
        'goback': 'panel_cliente_listado'
    }

    return render(request, 'paneltrabajador/eliminar_generico.html', contexto)
