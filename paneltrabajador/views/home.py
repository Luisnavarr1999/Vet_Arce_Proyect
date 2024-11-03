from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from paneltrabajador.models import Cita
from django.contrib.auth.forms import AuthenticationForm

def home(request):
    """
    Vista principal que redirige a la página de inicio del panel si el usuario está autenticado,
    de lo contrario, muestra el formulario de inicio de sesión.

    Args:
        request: La solicitud HTTP.

    Returns:
        HttpResponse: La respuesta HTTP que contiene la página de inicio del panel o el formulario de inicio de sesión.
    """
    # El usuario está autenticado, cargar home del panel
    if request.user.is_authenticated:
        # Cargar todas las citas
        citas = Cita.get_for_listado(usuario=request.user, estado='1')

        # Mostramos el grupo del usuario
        grupo = ""
        for g in request.user.groups.all():
            grupo += g.name.capitalize()

        # Variables para mostrarlas en el template
        context = {"username": request.user.username, "first_name": request.user.first_name, "last_name": request.user.last_name, "citas": citas, "grupo": grupo}
        return render(request, 'paneltrabajador/home.html', context)
    # No está autenticado, cargar login entonces
    else:
        # Envio de login
        if request.method == 'POST':
            form = AuthenticationForm(request=request, data=request.POST)

            # Es valido el formulario?
            if form.is_valid():
                # Hacer autentificacion
                username = form.cleaned_data.get("username")
                password = form.cleaned_data.get("password")
                user = authenticate(request, username=username, password=password)
                # Si el usuario existe entonces logear y redirigir al home
                if user is not None:
                    login(request, user)
                    return redirect('panel_home')
        else:
            # Asignar form para mostrarlo en el template
            form = AuthenticationForm()

        # Bootstrap 5 clases
        form.fields['username'].widget.attrs['class'] = 'form-control'
        form.fields['password'].widget.attrs['class'] = 'form-control'
        return render(request, 'paneltrabajador/login.html', {'form': form})

# Cierre de sesión Django Auth
def cerrar_sesion(request):
    """
    Cierra la sesión del usuario y redirige a la página de inicio.

    Args:
        request: La solicitud HTTP.

    Returns:
        HttpResponse: La respuesta HTTP que redirige a la página de inicio.
    """
    # El usuario no está autenticado, redireccionar al inicio
    if not request.user.is_authenticated:
        return redirect('panel_home')

    # Funcion logout de Django Auth
    logout(request)

    # Redigimos home, mostramos mensaje de exito
    messages.success(request, "Se ha cerrado su sesión.")
    return redirect('panel_home')
