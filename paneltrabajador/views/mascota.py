from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from paneltrabajador.forms import MascotaForm
from paneltrabajador.models import Mascota
from paneltrabajador.forms import MascotaDocumentoForm
from paneltrabajador.models import MascotaDocumento

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
    mascotas = Mascota.objects.all()
    return render(request, 'paneltrabajador/mascota/listado.html', {'mascotas': mascotas})

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
            for archivo in doc_form.cleaned_data['archivos']:
                MascotaDocumento.objects.create(mascota=mascota, archivo=archivo)

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
    documentos = mascota.documentos.all()

    if request.method == 'POST':
        # Form principal + form de archivos
        form = MascotaForm(request.POST, instance=mascota)
        doc_form = MascotaDocumentoForm(request.POST, request.FILES)

        if form.is_valid() and doc_form.is_valid():
            # Guardar cambios de la mascota
            mascota = form.save()

            # Guardar cada archivo adjunto nuevo (si hay)
            for archivo in doc_form.cleaned_data['archivos']:
                MascotaDocumento.objects.create(mascota=mascota, archivo=archivo)

            messages.success(request, "Se ha editado la mascota correctamente.")
            return redirect('panel_mascota_listar')

    else:
        form = MascotaForm(instance=mascota)
        doc_form = MascotaDocumentoForm()

    # Render con ambos formularios y lista de documentos existentes
    return render(request, 'paneltrabajador/form_generico.html', {
        'form': form,
        'doc_form': doc_form,
        'mascota': mascota,
        'documentos': documentos,
    })


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
