from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from paneltrabajador.forms import CitaForm
from paneltrabajador.models import Cita
from django.utils import timezone

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
    return render(request, 'paneltrabajador/cita/listado.html', {'citas': citas, 'es_home': False,})

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

def cita_checkin(request, n_cita):
    """
    Marca una cita como 'Asistió' (check-in rápido desde el listado).
    Requiere autenticación y permiso change_cita.
    """
    if not request.user.is_authenticated:
        return redirect('panel_home')

    if not request.user.has_perm('paneltrabajador.change_cita'):
        messages.error(request, "No tiene los permisos para realizar esto.")
        return redirect('panel_home')

    cita = get_object_or_404(Cita, n_cita=n_cita)

    # Reglas: solo si estaba reservada y ya ocurrió
    if not (cita.estado == '1' and cita.fecha <= timezone.now()):
        messages.error(request, "Solo puedes hacer check-in cuando la cita fue 'Reservada' y ya ocurrió.")
        return redirect('panel_cita_listar')

    cita.asistencia = 'A'
    # Si agregaste auditoría en el modelo, guarda quién/cuándo:
    if hasattr(cita, 'checked_in_at'):
        cita.checked_in_at = timezone.now()
    if hasattr(cita, 'checked_in_by'):
        cita.checked_in_by = request.user

    # Guarda (si tienes auditoría, optimiza con update_fields)
    fields = ['asistencia']
    if hasattr(cita, 'checked_in_at'):
        fields.append('checked_in_at')
    if hasattr(cita, 'checked_in_by'):
        fields.append('checked_in_by')
    cita.save(update_fields=fields)

    messages.success(request, "Asistencia registrada (check-in).")
    return redirect('panel_cita_listar')


def cita_noasistio(request, n_cita):
    """
    Marca una cita como 'No asistió' (rápido desde el listado).
    Requiere autenticación y permiso change_cita.
    """
    if not request.user.is_authenticated:
        return redirect('panel_home')

    if not request.user.has_perm('paneltrabajador.change_cita'):
        messages.error(request, "No tiene los permisos para realizar esto.")
        return redirect('panel_home')

    cita = get_object_or_404(Cita, n_cita=n_cita)

    # Reglas: solo si estaba reservada y ya ocurrió
    if not (cita.estado == '1' and cita.fecha <= timezone.now()):
        messages.error(request, "Solo puedes marcar 'No asistió' cuando la cita fue 'Reservada' y ya ocurrió.")
        return redirect('panel_cita_listar')

    cita.asistencia = 'N'
    cita.save(update_fields=['asistencia'])

    messages.success(request, "Marcado como 'No asistió'.")
    return redirect('panel_cita_listar')
