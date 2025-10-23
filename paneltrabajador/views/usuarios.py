from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from paneltrabajador.forms import UsuarioForm
from django.db import transaction
from django.core.mail import EmailMultiAlternatives
from django.templatetags.static import static

def usuario_listar(request):
    """
    Lista todos los usuarios si el usuario está autenticado y tiene los permisos necesarios.

    Args:
        request: La solicitud HTTP.

    Returns:
        HttpResponse: La respuesta HTTP que contiene la página de listado de usuarios o redirige al inicio.
    """
    # El usuario no está autenticado, redireccionar al inicio
    if not request.user.is_authenticated:
        return redirect('panel_home')

    # El usuario no tiene los permisos necesarios, redireccionar al home con un mensaje de error
    if not request.user.has_perm('auth.view_user'):
        messages.error(request, "No tiene los permisos para realizar esto.")
        return redirect('panel_home')

    # Obtenemos todos los objetos del modelo
    usuarios = get_user_model().objects.all()
    return render(request, 'paneltrabajador/usuario/listado.html', {'usuarios': usuarios})


def usuario_agregar(request):
    """
    Agrega un nuevo usuario si el usuario está autenticado y tiene los permisos necesarios.

    Args:
        request: La solicitud HTTP.

    Returns:
        HttpResponse: La respuesta HTTP que contiene el formulario de usuario o redirige al inicio.
    """
    # El usuario no está autenticado, redireccionar al inicio
    if not request.user.is_authenticated:
        return redirect('panel_home')

    # El usuario no tiene los permisos necesarios, redireccionar al home con un mensaje de error
    if not request.user.has_perm('auth.add_user'):
        messages.error(request, "No tiene los permisos para realizar esto.")
        return redirect('panel_home')

    # Se ha enviado el formulario
    if request.method == 'POST':
        # Pasar los datos de la peticion al formulario para la validacion
        form = UsuarioForm(request.POST)
        # Todo Ok?
        if form.is_valid():
            # Agregar nuevo objeto y asignarlo inmediatamente en una variable
            # Para trabajar con el más abajo
            nuevo_user = form.save()

            # Le asignamos el grupo ya que el select de Rol es personalizado del formulario
            # Pero no existe en el modelo como tal
            group = Group.objects.get(name=form.cleaned_data.get("rol_usuario"))
            nuevo_user.groups.add(group)

            # Ahora guardamos el usuario
            nuevo_user.save()

            # Redirige a la página de listado después de agregar un nuevo objeto
            messages.success(request, "Se ha agregado el usuario.")
            return redirect('panel_usuario_listar')
    else:
        form = UsuarioForm()

    return render(request, 'paneltrabajador/form_generico.html', {'form': form})

def usuario_editar(request, id_usuario):
    """
    Edita un usuario existente si el usuario está autenticado y tiene los permisos necesarios.

    Args:
        request: La solicitud HTTP.
        id_usuario: El ID del usuario a editar.

    Returns:
        HttpResponse: La respuesta HTTP que contiene el formulario de edición de usuario o redirige al inicio.
    """
    # El usuario no está autenticado, redireccionar al inicio
    if not request.user.is_authenticated:
        return redirect('panel_home')

    # El usuario no tiene los permisos necesarios, redireccionar al home con un mensaje de error
    if not request.user.has_perm('auth.change_user'):
        messages.error(request, "No tiene los permisos para realizar esto.")
        return redirect('panel_home')

    # Existe? Entonces asignar. No existe? Entonces mostrar un error 404.
    usuario = get_object_or_404(get_user_model(), id=id_usuario)

    # Se ha enviado el formulario
    if request.method == 'POST':
        # Pasar los datos de la peticion al formulario para la validacion
        # Aparte le pasamos el objeto para que pueda saber que estamos editando ese objeto en particular
        # En el caso de que no asignaramos instance, pensará que debemos agregar un objeto nuevo
        form = UsuarioForm(request.POST, instance=usuario)

        # Es valido el formulario? Ok.
        if form.is_valid():
            # Guardamos el usuario pero no cometemos la informacion a la base de datos
            # Si no que simplemente lo dejamos asignado
            nuevo_user = form.save(commit=False)

            # Limpiar todos los grupos que tenga
            nuevo_user.groups.clear()

            # Le asignamos el grupo ya que el select de Rol es personalizado del formulario
            # Pero no existe en el modelo como tal
            group = Group.objects.get(name=form.cleaned_data.get("rol_usuario"))
            nuevo_user.groups.add(group)

            # Finalmente guardamos y cometemos a la base de datos
            nuevo_user.save()

            # Redirige a la página de listado después de editar
            messages.success(request, "Se ha editado el usuario.")
            return redirect('panel_usuario_listar')
    else:
        form = UsuarioForm(instance=usuario)

    return render(request, 'paneltrabajador/form_generico.html', {'form': form, 'usuario': usuario})

def usuario_eliminar(request, id_usuario):
    """
    Elimina un usuario si el usuario está autenticado y tiene los permisos necesarios.

    Args:
        request: La solicitud HTTP.
        id_usuario: El ID del usuario a eliminar.

    Returns:
        HttpResponse: La respuesta HTTP que contiene la confirmación de eliminación o redirige al inicio.
    """
    # El usuario no está autenticado, redireccionar al inicio
    if not request.user.is_authenticated:
        return redirect('panel_home')

    # El usuario no tiene los permisos necesarios, redireccionar al home con un mensaje de error
    if not request.user.has_perm('auth.delete_user'):
        messages.error(request, "No tiene los permisos para realizar esto.")
        return redirect('panel_home')

    # Verificacion para que no se pueda eliminar el mismo.
    if id_usuario == request.user.id:
        messages.error(request, "No puede borrarse a usted mismo.")
        return redirect('panel_usuario_listar')

        # Existe? Entonces asignar. No existe? Entonces mostrar un error 404.
    user = get_object_or_404(get_user_model(), id=id_usuario)

    # El usuario hizo click en OK entonces envio el formulario
    if request.method == 'POST':
        # Eliminar objeto
        user.delete()
        # Redirige a la página de listado después de eliminar
        messages.success(request, "Se ha eliminado el usuario correctamente.")
        return redirect('panel_usuario_listar')

    # Asignar contexto para las variables en el template generico
    contexto = {
        'titulo': 'Eliminar Usuario',
        'descripcion': '¿Está seguro de que desea eliminar el usuario/trabajador con ID {} y nombre "{}"?'.format(user.id, user.get_username()),
        'goback': 'panel_usuario_listar'
    }
    return render(request, 'paneltrabajador/eliminar_generico.html', contexto)

def usuario_newpassword(request, id_usuario):
    """
    Genera y envía una nueva contraseña a un usuario si el usuario está autenticado y tiene los permisos necesarios.
    """
    # Validaciones de autenticación y permisos
    if not request.user.is_authenticated:
        return redirect('panel_home')

    if not request.user.has_perm('auth.change_user'):
        messages.error(request, "No tiene los permisos para realizar esto.")
        return redirect('panel_home')

    # Buscar usuario o lanzar error 404
    user = get_object_or_404(get_user_model(), id=id_usuario)

    try:
        # Generar nueva contraseña aleatoria
        raw_password = get_user_model().objects.make_random_password()

        # logo
        logo_url = "https://i.postimg.cc/x1RJ1G0t/Logovetarce.png"

        # Asunto y cuerpo
        subject = "Nueva contraseña – Veterinaria de Arce 🐾"
        text_body = (
            f"Hola {user.get_username()},\n\n"
            f"Se ha generado una nueva contraseña para tu cuenta en el sistema Veterinaria de Arce.\n"
            f"Tu nueva contraseña es: {raw_password}\n\n"
            f"Por seguridad, cámbiala al iniciar sesión.\n\n"
            f"— Veterinaria de Arce"
        )

        # Versión HTML con logo
        html_body = f"""
        <div style="font-family:Arial,Helvetica,sans-serif; color:#333; line-height:1.6; max-width:600px; margin:auto; border:1px solid #e0e0e0; border-radius:10px; padding:20px;">
            <div style="text-align:center; margin-bottom:20px;">
                <img src="{logo_url}" alt="Logo Veterinaria de Arce" style="width:120px; height:auto;">
            </div>
            <h2 style="color:#1a73e8; text-align:center;">Nueva Contraseña Generada</h2>
            <p>Hola <strong>{user.get_username()}</strong>,</p>
            <p>Se ha generado una nueva contraseña para tu cuenta en <b>Veterinaria de Arce</b>.</p>
            <p><b>Tu nueva contraseña:</b> 
                <span style="background:#f0f0f0; padding:6px 12px; border-radius:6px; font-weight:bold; display:inline-block;">
                    {raw_password}
                </span>
            </p>
            <p>Por seguridad, te recomendamos cambiarla al iniciar sesión.</p>
            <hr style="margin:20px 0; border:none; border-top:1px solid #ddd;">
            <p style="text-align:center; font-size:14px; color:#555;">
                — Equipo de <strong>Veterinaria de Arce 🐾</strong><br>
                <a href="https://tusitio.cl" style="color:#1a73e8; text-decoration:none;">www.veterinariadearce.cl</a>
            </p>
        </div>
        """

        # Crear y enviar el correo
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,  # ✅ Remitente verificado
            to=[user.email],
            headers={"Reply-To": "shadowxd41@gmail.com"},
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=False)

        # Actualizar la contraseña solo si el correo se envió con éxito
        user.set_password(raw_password)
        user.save(update_fields=["password"])

        messages.success(request, "Se ha enviado una nueva contraseña por correo al usuario.")
    
    except Exception as e:
        print(f"Error al enviar correo de nueva contraseña: {e}")
        messages.error(request, "Ha ocurrido un error y no se ha podido enviar la nueva contraseña.")

    return redirect('panel_usuario_listar')