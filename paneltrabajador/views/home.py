from datetime import datetime, timedelta, time

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Exists, OuterRef
from django.shortcuts import redirect, render
from django.utils import timezone

from paneltrabajador.models import Cita, EvolucionClinica, UserProfile


def home(request):
    """Vista principal del panel de trabajadores."""
    # Si el usuario está autenticado, cargar el panel
    if request.user.is_authenticated:

        # Grupos del usuario como cadena legible
        grupos_usuario = list(request.user.groups.values_list('name', flat=True))
        grupo = ", ".join(nombre.capitalize() for nombre in grupos_usuario)
        grupo_legible = grupo if grupo else "Sin rol asignado"

        nombre_completo = request.user.get_full_name().strip()
        display_name = nombre_completo if nombre_completo else request.user.username

        if nombre_completo:
            iniciales = "".join(part[0] for part in nombre_completo.split() if part)[:2].upper()
        else:
            iniciales = (request.user.username[:2] or "U").upper()

        try:
            perfil_usuario = request.user.panel_profile  # type: ignore[attr-defined]
        except UserProfile.DoesNotExist:
            perfil_usuario = None

        # ¿Tiene rol de recepcionista?
        es_recepcionista = any(nombre.lower() == 'recepcionista' for nombre in grupos_usuario)

        # Contexto adicional para recepcionista
        resumen_recepcionista = {}
        proximas_citas = []
        pendientes_checkin = []
        citas = []
        proxima_cita = None
        filtro_activo = request.GET.get('filtro', '').strip().lower()
        estadisticas_hoy = {
            "total": 0,
            "completadas": 0,
            "pendientes_informe": 0,
        }

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

        else:
            zona = timezone.get_current_timezone()
            ahora = timezone.localtime()
            hoy = ahora.date()

            citas_queryset = (
                Cita.objects.filter(usuario=request.user, estado='1')
                .select_related('cliente', 'mascota')
            )

            proxima_cita = (
                citas_queryset
                .filter(fecha__gte=ahora)
                .order_by('fecha')
                .first()
            )

            evoluciones_por_cita = EvolucionClinica.objects.filter(cita=OuterRef('pk'))

            if filtro_activo == 'hoy':
                citas_queryset = citas_queryset.filter(fecha__date=hoy)
            elif filtro_activo == 'proximas':
                citas_queryset = citas_queryset.filter(fecha__gte=ahora)
            elif filtro_activo == 'pendientes':
                citas_queryset = (
                    citas_queryset
                    .filter(asistencia='A')
                    .annotate(tiene_informe=Exists(evoluciones_por_cita))
                    .filter(tiene_informe=False)
                )

            citas_ordenadas = list(citas_queryset.order_by('-fecha'))


            for cita in citas_ordenadas:
                indicadores = []
                minutos_para_inicio = None

                if cita.fecha is not None:
                    try:
                        fecha_local = timezone.localtime(cita.fecha, timezone=zona)
                    except ValueError:
                        fecha_local = cita.fecha
                    diferencia = fecha_local - ahora
                    minutos_para_inicio = diferencia.total_seconds() / 60

                    if minutos_para_inicio >= 0:
                        if minutos_para_inicio < 10:
                            indicadores.append({
                                'texto': 'Menos de 10 minutos',
                                'tipo': 'danger',
                            })
                        elif minutos_para_inicio < 60:
                            indicadores.append({
                                'texto': 'Comienza pronto',
                                'tipo': 'warning',
                            })

                servicio = (cita.servicio or '').lower()
                if servicio == 'cirugia':
                    indicadores.append({
                        'texto': 'Cirugía',
                        'tipo': 'primary',
                    })
                elif 'control' in servicio:
                    indicadores.append({
                        'texto': 'Control',
                        'tipo': 'success',
                    })

                cita.indicadores = indicadores
                cita.minutos_para_inicio = minutos_para_inicio

            citas = citas_ordenadas

            citas_hoy = Cita.objects.filter(
                usuario=request.user,
                estado='1',
                fecha__date=hoy,
            )

            estadisticas_hoy["total"] = citas_hoy.count()
            estadisticas_hoy["completadas"] = citas_hoy.filter(asistencia='A').count()
            estadisticas_hoy["pendientes_informe"] = (
                citas_hoy
                .filter(asistencia='A')
                .annotate(tiene_informe=Exists(evoluciones_por_cita))
                .filter(tiene_informe=False)
                .count()
            )
            

        # Variables para el template
        context = {
            "username": request.user.username,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "display_name": display_name,
            "citas": citas,
            "proxima_cita": proxima_cita,
            "filtro_activo": filtro_activo,
            "estadisticas_hoy": estadisticas_hoy,
            "grupo": grupo_legible,
            "grupo": grupo,
            "es_recepcionista": es_recepcionista,
            "resumen_recepcionista": resumen_recepcionista,
            "proximas_citas": proximas_citas,
            "pendientes_checkin": pendientes_checkin,
            "profile_photo_url": perfil_usuario.photo_url if perfil_usuario else None,
            "avatar_initials": iniciales or "U",
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
