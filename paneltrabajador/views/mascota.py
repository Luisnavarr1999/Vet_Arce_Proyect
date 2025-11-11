from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags
from django.db.models import Q
from urllib.parse import urljoin

from paneltrabajador.forms import EvolucionClinicaForm, MascotaDocumentoForm, MascotaForm
from paneltrabajador.models import EvolucionClinica, Mascota, MascotaDocumento


# para poder usarlo en los correo o si queremos listar
def _formatear_rut_con_dv(rut):
    """Devuelve el RUT con guion y dígito verificador calculado."""

    rut_str = str(rut)
    factores = [2, 3, 4, 5, 6, 7]
    total = 0

    for indice, digito in enumerate(reversed(rut_str)):
        total += int(digito) * factores[indice % len(factores)]

    resto = total % 11
    dv = 11 - resto

    if dv == 11:
        dv_str = "0"
    elif dv == 10:
        dv_str = "K"
    else:
        dv_str = str(dv)

    return f"{rut_str}-{dv_str}"

def mascota_listar(request):
    """
    Lista todas las mascotas si el usuario está autenticado y tiene los permisos necesarios.

    Args:
        request: La solicitud HTTP.

    Returns:
        HttpResponse: La respuesta HTTP que contiene la página de listado de mascotas o redirige al inicio.
    """
    # El usuario no está autenticado, redireccionar al inicio
    if not request.user.is_authenticated:
        return redirect('panel_home')

    # El usuario no tiene los permisos necesarios, redireccionar al home con un mensaje de error
    if not request.user.has_perm('paneltrabajador.view_mascota'):
        messages.error(request, "No tiene los permisos para realizar esto.")
        return redirect('panel_home')

    # Obtenemos todos los objetos del modelo
    busqueda = request.GET.get('q', '').strip()
    mascotas = Mascota.objects.all().select_related('cliente')

    if busqueda:
        mascotas = mascotas.filter(
            Q(nombre__icontains=busqueda)
            | Q(numero_chip__icontains=busqueda)
            | Q(cliente__nombre_cliente__icontains=busqueda)
            | Q(cliente__rut__icontains=busqueda)
        )

    return render(
        request,
        'paneltrabajador/mascota/listado.html',
        {'mascotas': mascotas, 'busqueda': busqueda},
    )

def mascota_agregar(request):
    """
    Agrega una nueva mascota si el usuario está autenticado y tiene los permisos necesarios.

    Args:
        request: La solicitud HTTP.

    Returns:
        HttpResponse: La respuesta HTTP que contiene el formulario de mascota o redirige al inicio.
    """
     # El usuario no está autenticado → redireccionar al inicio
    if not request.user.is_authenticated:
        return redirect('panel_home')

    # El usuario no tiene permisos → mensaje y redirección
    if not request.user.has_perm('paneltrabajador.add_mascota'):
        messages.error(request, "No tiene los permisos para realizar esto.")
        return redirect('panel_home')

    # Si se envió el formulario
    if request.method == 'POST':
        form = MascotaForm(request.POST)
        doc_form = MascotaDocumentoForm(request.POST, request.FILES)

        if form.is_valid() and doc_form.is_valid():
            # Guardar la mascota
            mascota = form.save()

            # Guardar cada archivo adjunto
            evolucion = doc_form.cleaned_data.get('evolucion')
            for archivo in doc_form.cleaned_data['archivos']:
                MascotaDocumento.objects.create(
                    mascota=mascota,
                    archivo=archivo,
                    evolucion=evolucion,
                )

            messages.success(request, "Se ha agregado la mascota correctamente.")
            return redirect('panel_mascota_listar')

    else:
        # Mostrar formulario vacío si es GET
        form = MascotaForm()
        doc_form = MascotaDocumentoForm()

    # Renderizar con ambos formularios
    return render(request, 'paneltrabajador/form_generico.html', {
        'form': form,
        'doc_form': doc_form,
    })

def mascota_editar(request, id_mascota):
    """
    Edita una mascota existente si el usuario está autenticado y tiene los permisos necesarios.

    Args:
        request: La solicitud HTTP.
        id_mascota: El ID de la mascota a editar.

    Returns:
        HttpResponse: La respuesta HTTP que contiene el formulario de edición de mascota o redirige al inicio.
    """
    # El usuario no está autenticado → redireccionar al inicio
    if not request.user.is_authenticated:
        return redirect('panel_home')

    # El usuario no tiene permisos → mensaje y redirección
    if not request.user.has_perm('paneltrabajador.change_mascota'):
        messages.error(request, "No tiene los permisos para realizar esto.")
        return redirect('panel_home')

    # Obtener mascota o 404
    mascota = get_object_or_404(Mascota, id_mascota=id_mascota)

    # Para listar en el template los documentos ya existentes
    documentos = mascota.documentos.filter(evolucion__isnull=True)

    if request.method == 'POST':
        # Form principal + form de archivos
        form = MascotaForm(request.POST, instance=mascota)
        doc_form = MascotaDocumentoForm(request.POST, request.FILES, mascota=mascota)

        if form.is_valid() and doc_form.is_valid():
            # Guardar cambios de la mascota
            mascota = form.save()

            # Guardar cada archivo adjunto nuevo (si hay)
            evolucion = doc_form.cleaned_data.get('evolucion')
            for archivo in doc_form.cleaned_data['archivos']:
                MascotaDocumento.objects.create(
                    mascota=mascota,
                    archivo=archivo,
                    evolucion=evolucion,
                )

            messages.success(request, "Se ha editado la mascota correctamente.")
            return redirect('panel_mascota_listar')

    else:
        form = MascotaForm(instance=mascota)
        doc_form = MascotaDocumentoForm(mascota=mascota)

    # Render con ambos formularios y lista de documentos existentes
    return render(request, 'paneltrabajador/form_generico.html', {
        'form': form,
        'doc_form': doc_form,
        'mascota': mascota,
        'documentos': documentos,
    })

def mascota_historial(request, id_mascota):
    """Permite registrar y revisar las evoluciones clínicas de una mascota."""

    if not request.user.is_authenticated:
        return redirect('panel_home')

    if not request.user.has_perm('paneltrabajador.change_mascota'):
        messages.error(request, "No tiene los permisos para realizar esto.")
        return redirect('panel_home')

    mascota = get_object_or_404(Mascota, id_mascota=id_mascota)
    evoluciones = (
        mascota.evoluciones.select_related('cita', 'cita__usuario')
        .prefetch_related('documentos')
    )

    if request.method == 'POST':
        form = EvolucionClinicaForm(request.POST, request.FILES, mascota=mascota)
        if not form.has_citas_disponibles:
            messages.error(
                request,
                "La mascota no tiene citas registradas. Registra una cita antes de añadir una evolución clínica.",
            )
        elif form.is_valid():
            evolucion = form.save(commit=False)
            evolucion.mascota = mascota
            if evolucion.cita and not evolucion.servicio:
                evolucion.servicio = evolucion.cita.servicio
            evolucion.save()

            for archivo in form.cleaned_data['archivos']:
                MascotaDocumento.objects.create(
                    mascota=mascota,
                    archivo=archivo,
                    evolucion=evolucion,
                )

            messages.success(request, "Se registró una nueva evolución clínica.")
            return redirect('panel_mascota_historial', id_mascota=mascota.id_mascota)
    else:
        form = EvolucionClinicaForm(mascota=mascota)

    servicios_por_cita = {
        str(cita.pk): {
            'codigo': cita.servicio,
            'nombre': cita.get_servicio_display(),
        }
        for cita in form.fields['cita'].queryset
    }

    servicio_inicial = None
    if form.is_bound:
        cita_value = form['cita'].value()
        if cita_value:
            servicio_inicial = servicios_por_cita.get(str(cita_value), {}).get('nombre')

    return render(
        request,
        'paneltrabajador/mascota/historial.html',
        {
            'mascota': mascota,
            'evoluciones': evoluciones,
            'form': form,
            'servicios_por_cita': servicios_por_cita,
            'servicio_inicial': servicio_inicial,
        },
    )


def mascota_eliminar(request, id_mascota):
    """
    Elimina una mascota si el usuario está autenticado y tiene los permisos necesarios.

    Args:
        request: La solicitud HTTP.
        id_mascota: El ID de la mascota a eliminar.

    Returns:
        HttpResponse: La respuesta HTTP que contiene la confirmación de eliminación o redirige al inicio.
    """
    # El usuario no está autenticado, redireccionar al inicio
    if not request.user.is_authenticated:
        return redirect('panel_home')

    # El usuario no tiene los permisos necesarios, redireccionar al home con un mensaje de error
    if not request.user.has_perm('paneltrabajador.delete_mascota'):
        messages.error(request, "No tiene los permisos para realizar esto.")
        return redirect('panel_home')

    # Existe? Entonces asignar. No existe? Entonces mostrar un error 404.
    mascota = get_object_or_404(Mascota, id_mascota=id_mascota)

    # El usuario hizo click en OK entonces envio el formulario
    if request.method == 'POST':
        # Eliminar objeto
        mascota.delete()
        # Redirige a la página de listado después de eliminar
        messages.success(request, "Se ha eliminado la mascota correctamente.")
        return redirect('panel_mascota_listar')

    # Asignar contexto para las variables en el template generico
    contexto = {
        'titulo': 'Eliminar Mascota',
        'descripcion': '¿Está seguro de que desea eliminar la mascota con ID {} y nombre "{}"?'.format(mascota.id_mascota, mascota.nombre),
        'goback': 'panel_mascota_listar'
    }

    return render(request, 'paneltrabajador/eliminar_generico.html', contexto)

def mascota_enviar_recordatorio(request, id_mascota):
    """Envía un recordatorio al cliente con los datos de consulta de la mascota."""

    if not request.user.is_authenticated:
        return redirect('panel_home')

    if not request.user.has_perm('paneltrabajador.change_mascota'):
        messages.error(request, "No tiene los permisos para realizar esto.")
        return redirect('panel_home')

    mascota = get_object_or_404(Mascota, id_mascota=id_mascota)

    if request.method != 'POST':
        messages.warning(request, "Para enviar un recordatorio debe utilizar el botón correspondiente.")
        return redirect('panel_mascota_listar')

    path_consulta = reverse('ambpublico_consulta')

    if getattr(settings, "PUBLIC_BASE_URL", ""):
        consulta_url = urljoin(settings.PUBLIC_BASE_URL + "/", path_consulta.lstrip("/"))
    else:
        consulta_url = request.build_absolute_uri(path_consulta)

    contexto_email = {
        'mascota': mascota,
        'cliente': mascota.cliente,
        'consulta_url': consulta_url,
        'site_name': 'Veterinaria de Arce',
        'logo_url': 'https://i.postimg.cc/x1RJ1G0t/Logovetarce.png',
        'primary_color': '#1a73e8',
        'website_url': 'https://www.veterinariadearce.cl',
        'cliente_rut_formateado': _formatear_rut_con_dv(mascota.cliente.rut),
    }

    asunto = "Ficha clínica actualizada de {}".format(mascota.nombre)
    cuerpo_html = render_to_string('paneltrabajador/emails/mascota_recordatorio.html', contexto_email)
    cuerpo_texto = strip_tags(cuerpo_html)

    mensaje = EmailMultiAlternatives(
        subject=asunto,
        body=cuerpo_texto,
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
        to=[mascota.cliente.email],
    )
    mensaje.attach_alternative(cuerpo_html, 'text/html')

    try:
        mensaje.send()
        messages.success(request, "Se ha enviado el recordatorio al cliente {}.".format(mascota.cliente.nombre_cliente))
    except Exception:
        messages.error(request, "No se pudo enviar el correo de recordatorio. Inténtelo nuevamente más tarde.")

    return redirect('panel_mascota_listar')

@require_POST
def mascota_doc_eliminar(request, id_mascota, doc_id):
    """
    Elimina un documento adjunto de una mascota.
    Permisos: usuario autenticado y con change_mascota o delete_mascotadocumento.
    """
    if not request.user.is_authenticated:
        return redirect('panel_home')

    if not (
        request.user.has_perm('paneltrabajador.change_mascota')
        or request.user.has_perm('paneltrabajador.delete_mascotadocumento')
    ):
        messages.error(request, "No tiene los permisos para realizar esto.")
        return redirect('panel_home')

    mascota = get_object_or_404(Mascota, id_mascota=id_mascota)
    documento = get_object_or_404(MascotaDocumento, pk=doc_id, mascota=mascota)
    pertenece_a_evolucion = documento.evolucion_id is not None

    # Borra (esto también elimina el archivo físico por el método delete() del modelo)
    documento.delete()
    messages.success(request, "Documento eliminado correctamente.")

    if pertenece_a_evolucion:
        return redirect('panel_mascota_historial', id_mascota=mascota.id_mascota)

    return redirect('panel_mascota_editar', id_mascota=mascota.id_mascota)
