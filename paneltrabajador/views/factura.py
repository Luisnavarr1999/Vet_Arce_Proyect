from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from paneltrabajador.forms import FacturaForm
from paneltrabajador.models import Factura
def factura_listar(request):
    """
    Muestra un listado de todas las facturas.

    Verifica la autenticación del usuario y sus permisos antes de mostrar la información.

    Args:
        request: La solicitud HTTP.

    Returns:
        HttpResponse: La respuesta HTTP que contiene el listado de facturas.
    """
    # El usuario no está autenticado, redireccionar al inicio
    if not request.user.is_authenticated:
        return redirect('panel_home')

    # El usuario no tiene los permisos necesarios, redireccionar al home con un mensaje de error
    if not request.user.has_perm('paneltrabajador.view_factura'):
        messages.error(request, "No tiene los permisos para realizar esto.")
        return redirect('panel_home')

    # Obtenemos todos los objetos del modelo
    facturas = Factura.objects.all()
    return render(request, 'paneltrabajador/factura/listado.html', {'facturas': facturas})

def factura_agregar(request):
    """
    Permite agregar una nueva factura.

    Verifica la autenticación y los permisos del usuario.
    Si se envía el formulario correctamente, se guarda la nueva factura
    y se redirige al listado de facturas.

    Args:
        request: La solicitud HTTP.

    Returns:
        HttpResponse: La respuesta HTTP que contiene el formulario de creación o el listado de facturas.
    """
    # El usuario no está autenticado, redireccionar al inicio
    if not request.user.is_authenticated:
        return redirect('panel_home')

    # El usuario no tiene los permisos necesarios, redireccionar al home con un mensaje de error
    if not request.user.has_perm('paneltrabajador.add_factura'):
        messages.error(request, "No tiene los permisos para realizar esto.")
        return redirect('panel_home')

    # Se ha enviado el formulario
    if request.method == 'POST':
        # Pasar los datos de la peticion al formulario para la validacion
        form = FacturaForm(request.POST)
        # Todo Ok?
        if form.is_valid():
            # Agregar nuevo objeto
            form.save()
            # Redirige a la página de listado después de agregar un nuevo objeto
            messages.success(request, "Se ha agregado la factura correctamente.")
            return redirect('panel_factura_listar')
    else:
        # Asignar form para mostrarlo en el template
        form = FacturaForm()

    return render(request, 'paneltrabajador/form_generico.html', {'form': form})

def factura_editar(request, numero_factura):
    """
    Permite editar una factura existente.

    Verifica la autenticación y los permisos del usuario.
    Si se envía el formulario correctamente, se actualiza la factura
    y se redirige al listado de facturas.

    Args:
        request: La solicitud HTTP.
        numero_factura: El número de factura que se va a editar.

    Returns:
        HttpResponse: La respuesta HTTP que contiene el formulario de edición o el listado de facturas.
    """
    # El usuario no está autenticado, redireccionar al inicio
    if not request.user.is_authenticated:
        return redirect('panel_home')

    # El usuario no tiene los permisos necesarios, redireccionar al home con un mensaje de error
    if not request.user.has_perm('paneltrabajador.change_factura'):
        messages.error(request, "No tiene los permisos para realizar esto.")
        return redirect('panel_home')

    # Existe? Entonces asignar. No existe? Entonces mostrar un error 404.
    factura = get_object_or_404(Factura, numero_factura=numero_factura)
    # Se ha enviado el formulario
    if request.method == 'POST':
        # Pasar los datos de la peticion al formulario para la validacion
        # Aparte le pasamos el objeto para que pueda saber que estamos editando ese objeto en particular
        # En el caso de que no asignaramos instance, pensará que debemos agregar un objeto nuevo
        form = FacturaForm(request.POST, instance=factura)
        # Todo Ok?
        if form.is_valid():
            # Guardar
            form.save()
            # Redirige a la página de listado después de editar
            messages.success(request, "Se ha editado la factura correctamente.")
            return redirect('panel_factura_listar')
    else:
        # Asignar form para mostrarlo en el template
        form = FacturaForm(instance=factura)

    return render(request, 'paneltrabajador/form_generico.html', {'form': form, 'factura': factura})

def factura_eliminar(request, numero_factura):
    """
    Permite eliminar una factura existente.

    Verifica la autenticación y los permisos del usuario.
    Si se confirma la eliminación, se borra la factura
    y se redirige al listado de facturas.

    Args:
        request: La solicitud HTTP.
        numero_factura: El número de factura que se va a eliminar.

    Returns:
        HttpResponse: La respuesta HTTP que contiene el formulario de confirmación o el listado de facturas.
    """
    # El usuario no está autenticado, redireccionar al inicio
    if not request.user.is_authenticated:
        return redirect('panel_home')

    # El usuario no tiene los permisos necesarios, redireccionar al home con un mensaje de error
    if not request.user.has_perm('paneltrabajador.delete_factura'):
        messages.error(request, "No tiene los permisos para realizar esto.")
        return redirect('panel_home')

    # Existe? Entonces asignar. No existe? Entonces mostrar un error 404.
    factura = get_object_or_404(Factura, numero_factura=numero_factura)

    # El usuario hizo click en OK entonces envio el formulario
    if request.method == 'POST':
        # Eliminar objeto
        factura.delete()
        # Redirige a la página de listado después de eliminar
        messages.success(request, "Se ha eliminado la factura correctamente.")
        return redirect('panel_factura_listar')

    # Asignar contexto para las variables en el template generico
    contexto = {
        'titulo': 'Eliminar Factura',
        'descripcion': '¿Está seguro de que desea eliminar la factura N°{} del cliente "{}"?'.format(factura.numero_factura, factura.cliente),
        'goback': 'panel_factura_listar'
    }

    return render(request, 'paneltrabajador/eliminar_generico.html', contexto)
