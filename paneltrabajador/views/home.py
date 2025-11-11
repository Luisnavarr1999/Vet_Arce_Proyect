from datetime import datetime, timedelta, time

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from django.utils import timezone

from paneltrabajador.models import Cita


def home(request):
    """Vista principal del panel de trabajadores."""
    # Si el usuario está autenticado, cargar el panel
    if request.user.is_authenticated:
        # Cargar todas las citas del usuario (para profesionales)
        citas = Cita.get_for_listado(usuario=request.user, estado='1')

        # Grupos del usuario como cadena legible
        grupos_usuario = list(request.user.groups.values_list('name', flat=True))
        grupo = ", ".join(nombre.capitalize() for nombre in grupos_usuario)

        # ¿Tiene rol de recepcionista?
        es_recepcionista = any(nombre.lower() == 'recepcionista' for nombre in grupos_usuario)

        # Contexto adicional para recepcionista
        resumen_recepcionista = {}
        proximas_citas = []
        pendientes_checkin = []

        if es_recepcionista:
            # Fecha y hora actual
            hoy = timezone.localdate()
            ahora = timezone.localtime()
            ventana_alerta = ahora + timedelta(hours=2)

            # Crear rango horario preciso para el día actual
            zona = timezone.get_current_timezone()
            inicio_dia = datetime.combine(hoy, time.min)
            fin_dia = inicio_dia + timedelta(days=1)

            # Asegurar que sean datetime “aware”
            if timezone.is_naive(inicio_dia):
                inicio_dia = timezone.make_aware(inicio_dia, zona)
            if timezone.is_naive(fin_dia):
                fin_dia = timezone.make_aware(fin_dia, zona)

            # Filtrar citas de hoy con rango exacto
            citas_hoy = Cita.objects.filter(fecha__gte=inicio_dia, fecha__lt=fin_dia)

            # Resumen general del día
            resumen_recepcionista = {
                "reservadas": citas_hoy.filter(estado='1').count(),
                "checkins_pendientes": citas_hoy.filter(estado='1', asistencia='P').count(),
                "canceladas": citas_hoy.filter(estado='2').count(),
                "atendidas": citas_hoy.filter(estado='1', asistencia='A').count(),
            }

            # Próximas llegadas (citas del día aún no iniciadas)
            proximas_citas = (
                citas_hoy.filter(estado='1', fecha__gte=ahora)
                .select_related('cliente', 'mascota')
                .order_by('fecha')[:5]
            )

            # Citas pendientes de check-in en las próximas 2 horas
            pendientes_checkin = (
                citas_hoy.filter(
                    estado='1',
                    asistencia='P',
                    fecha__gte=ahora,
                    fecha__lte=ventana_alerta,
                )
                .select_related('cliente', 'mascota')
                .order_by('fecha')[:5]
            )

        # Variables para el template
        context = {
            "username": request.user.username,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "citas": citas,
            "grupo": grupo,
            "es_recepcionista": es_recepcionista,
            "resumen_recepcionista": resumen_recepcionista,
            "proximas_citas": proximas_citas,
            "pendientes_checkin": pendientes_checkin,
        }
        return render(request, 'paneltrabajador/home.html', context)

    # Si no está autenticado, mostrar login
    else:
        if request.method == 'POST':
            form = AuthenticationForm(request=request, data=request.POST)

            # Validar formulario
            if form.is_valid():
                username = form.cleaned_data.get("username")
                password = form.cleaned_data.get("password")
                user = authenticate(request, username=username, password=password)

                # Si el usuario existe, iniciar sesión
                if user is not None:
                    login(request, user)
                    return redirect('panel_home')
        else:
            # Mostrar formulario vacío
            form = AuthenticationForm()

        # Clases Bootstrap 5
        form.fields['username'].widget.attrs['class'] = 'form-control'
        form.fields['password'].widget.attrs['class'] = 'form-control'
        return render(request, 'paneltrabajador/login.html', {'form': form})


def cerrar_sesion(request):
    """
    Cierra la sesión del usuario y redirige a la página de inicio.
    """
    # Si no está autenticado, redirigir al inicio
    if not request.user.is_authenticated:
        return redirect('panel_home')

    # Cerrar sesión
    logout(request)

    # Mostrar mensaje de éxito y redirigir
    messages.success(request, "Se ha cerrado su sesión.")
    return redirect('panel_home')
