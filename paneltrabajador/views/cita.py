from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from paneltrabajador.forms import CitaForm
from paneltrabajador.models import Cita

def cita_listar(request):
    """
    Vista para listar todas las citas.

    Requiere que el usuario esté autenticado y tenga permisos para ver citas.

    :param request: Objeto HttpRequest.
    :return: HttpResponse con la lista de citas.
    """
    if not request.user.is_authenticated:
        return redirect('panel_home')

    # El usuario no tiene los permisos necesarios, redireccionar al home con un mensaje de error
    if not request.user.has_perm('paneltrabajador.view_cita'):
        messages.error(request, "No tiene los permisos para realizar esto.")
        return redirect('panel_home')

    # Obtenemos todos los objetos del modelo
    # Usamos la funcion personalizada del modelo
    citas = Cita.get_for_listado()
    return render(request, 'paneltrabajador/cita/listado.html', {'citas': citas})

def cita_agregar(request):
    """
    Vista para agregar una nueva cita.

    Requiere que el usuario esté autenticado y tenga permisos para agregar citas.

    :param request: Objeto HttpRequest.
    :return: HttpResponse con el formulario de agregar cita.
    """
    if not request.user.is_authenticated:
        return redirect('panel_home')

    # El usuario no tiene los permisos necesarios, redireccionar al home con un mensaje de error
    if not request.user.has_perm('paneltrabajador.add_cita'):
        messages.error(request, "No tiene los permisos para realizar esto.")
        return redirect('panel_home')

    # Se ha enviado el formulario
    if request.method == 'POST':
        # Pasar los datos de la peticion al formulario para la validacion
        form = CitaForm(request.POST)

        # Todo Ok?
        if form.is_valid():
            # Agregar nuevo objeto
            form.save()
            # Redirige a la página de listado después de agregar un nuevo objeto
            return redirect('panel_cita_listar')
    else:
        # Asignar form para mostrarlo en el template
        form = CitaForm()

    return render(request, 'paneltrabajador/form_generico.html', {'form': form})


def cita_editar(request, n_cita):
    """
    Vista para editar una cita existente.

    Requiere que el usuario esté autenticado y tenga permisos para editar citas.

    :param request: Objeto HttpRequest.
    :param n_cita: Número de la cita a editar.
    :return: HttpResponse con el formulario de editar cita.
    """
    if not request.user.is_authenticated:
        return redirect('panel_home')

    # El usuario no tiene los permisos necesarios, redireccionar al home con un mensaje de error
    if not request.user.has_perm('paneltrabajador.change_cita'):
        messages.error(request, "No tiene los permisos para realizar esto.")
        return redirect('panel_home')

    # Existe? Entonces asignar. No existe? Entonces mostrar un error 404.
    cita = get_object_or_404(Cita, n_cita=n_cita)

    # Se ha enviado el formulario
    if request.method == 'POST':
        # Pasar los datos de la peticion al formulario para la validacion
        # Aparte le pasamos el objeto para que pueda saber que estamos editando ese objeto en particular
        # En el caso de que no asignaramos instance, pensará que debemos agregar un objeto nuevo
        form = CitaForm(request.POST, instance=cita)

        # Todo Ok?
        if form.is_valid():
            # Guardar
            form.save()
            # Redirige a la página de listado después de editar
            return redirect('panel_cita_listar')
    else:
        # Asignar form para mostrarlo en el template
        form = CitaForm(instance=cita)

    return render(request, 'paneltrabajador/form_generico.html', {'form': form, 'cita': cita})


def cita_eliminar(request, n_cita):
    """
    Vista para eliminar una cita existente.

    Requiere que el usuario esté autenticado y tenga permisos para eliminar citas.

    :param request: Objeto HttpRequest.
    :param n_cita: Número de la cita a eliminar.
    :return: HttpResponse con el formulario de confirmación de eliminación.
    """
    if not request.user.is_authenticated:
        return redirect('panel_home')

    # El usuario no tiene los permisos necesarios, redireccionar al home con un mensaje de error
    if not request.user.has_perm('paneltrabajador.delete_cita'):
        messages.error(request, "No tiene los permisos para realizar esto.")
        return redirect('panel_home')

    # Existe? Entonces asignar. No existe? Entonces mostrar un error 404.
    cita = get_object_or_404(Cita, n_cita=n_cita)

    # El usuario hizo click en OK entonces envio el formulario
    if request.method == 'POST':
        # Eliminar objeto
        cita.delete()
        # Redirige a la página de listado después de eliminar
        return redirect('panel_cita_listar')

    # Asignar contexto para las variables en el template generico
    contexto = {
        'titulo': 'Eliminar Cita',
        'descripcion': '¿Está seguro que desea eliminar la cita {} con fecha {}? '.format(cita.n_cita, cita.fecha),
        'goback': 'panel_cita_listar'
    }

    return render(request, 'paneltrabajador/eliminar_generico.html', contexto)
