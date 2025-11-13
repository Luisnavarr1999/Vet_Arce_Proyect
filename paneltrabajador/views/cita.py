from datetime import datetime, time
from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
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

    # Parámetros de filtros (solo se aplican si son válidos)
    estado = request.GET.get('estado', '').strip()
    servicio = request.GET.get('servicio', '').strip()
    asistencia = request.GET.get('asistencia', '').strip()
    fecha_desde_raw = request.GET.get('fecha_desde', '').strip()
    fecha_hasta_raw = request.GET.get('fecha_hasta', '').strip()
    termino_busqueda = request.GET.get('q', '').strip()

    filtros_queryset = {}
    filtros_aplicados = []

    estado_labels = dict(Cita.ESTADO_CHOICES)
    asistencia_labels = dict(Cita.ASISTENCIA_CHOICES)
    servicio_labels = dict(Cita.SERVICIO_CHOICES)

    if estado and estado in estado_labels:
        filtros_queryset['estado'] = estado
        filtros_aplicados.append(f"Estado: {estado_labels[estado]}")

    if servicio and servicio in servicio_labels:
        filtros_queryset['servicio'] = servicio
        filtros_aplicados.append(f"Servicio: {servicio_labels[servicio]}")

    if asistencia and asistencia in asistencia_labels:
        filtros_queryset['asistencia'] = asistencia
        filtros_aplicados.append(f"Asistencia: {asistencia_labels[asistencia]}")

    citas = Cita.get_for_listado(**filtros_queryset)

    fecha_desde = None
    if fecha_desde_raw:
        try:
            fecha_desde = datetime.strptime(fecha_desde_raw, '%Y-%m-%d').date()
        except ValueError:
            fecha_desde_raw = ''
            fecha_desde = None

    fecha_hasta = None
    if fecha_hasta_raw:
        try:
            fecha_hasta = datetime.strptime(fecha_hasta_raw, '%Y-%m-%d').date()
        except ValueError:
            fecha_hasta_raw = ''
            fecha_hasta = None

    rango_invalido = False
    if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
        # Rango inválido: se ignoran ambos para evitar confusiones
        rango_invalido = True
        fecha_desde = None
        fecha_hasta = None
        fecha_desde_raw = ''
        fecha_hasta_raw = ''

    def _make_aware(fecha, limite):
        fecha_combinada = datetime.combine(fecha, limite)
        if settings.USE_TZ and timezone.is_naive(fecha_combinada):
            return timezone.make_aware(fecha_combinada, timezone.get_current_timezone())
        return fecha_combinada

    if fecha_desde:
        inicio_dia = _make_aware(fecha_desde, time.min)
        citas = citas.filter(fecha__gte=inicio_dia)
        filtros_aplicados.append(f"Desde: {fecha_desde.strftime('%d/%m/%Y')}")

    if fecha_hasta:
        fin_dia = _make_aware(fecha_hasta, time.max)
        citas = citas.filter(fecha__lte=fin_dia)
        filtros_aplicados.append(f"Hasta: {fecha_hasta.strftime('%d/%m/%Y')}")

    if rango_invalido:
        messages.warning(request, "El rango de fechas seleccionado es inválido. Se mostraron todas las citas sin filtrar por fecha.")

    if termino_busqueda:
        busqueda = termino_busqueda
        filtros_texto = Q(cliente__nombre_cliente__icontains=busqueda) | Q(mascota__nombre__icontains=busqueda) | Q(usuario__username__icontains=busqueda)

        try:
            numero_cita = int(busqueda)
        except ValueError:
            numero_cita = None

        if numero_cita is not None:
            filtros_texto |= Q(n_cita=numero_cita)

        citas = citas.filter(filtros_texto)
        filtros_aplicados.append(f'Búsqueda: "{busqueda}"')

    filtros_formulario = {
        'estado': estado,
        'servicio': servicio,
        'asistencia': asistencia,
        'fecha_desde': fecha_desde_raw,
        'fecha_hasta': fecha_hasta_raw,
        'q': termino_busqueda,
    }

    contexto = {
        'citas': citas,
        'es_home': False,
        'estado_choices': Cita.ESTADO_CHOICES,
        'servicio_choices': Cita.SERVICIO_CHOICES,
        'asistencia_choices': Cita.ASISTENCIA_CHOICES,
        'filtros': filtros_formulario,
        'filtros_aplicados': filtros_aplicados,
    }

    return render(request, 'paneltrabajador/cita/listado.html', contexto)

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
