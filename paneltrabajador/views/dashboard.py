import csv
from collections import defaultdict
from datetime import datetime, timedelta
from urllib.parse import urlencode

from django.contrib import messages
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from paneltrabajador.models import Cita


MESES_NOMBRES = [
    (1, 'Enero'),
    (2, 'Febrero'),
    (3, 'Marzo'),
    (4, 'Abril'),
    (5, 'Mayo'),
    (6, 'Junio'),
    (7, 'Julio'),
    (8, 'Agosto'),
    (9, 'Septiembre'),
    (10, 'Octubre'),
    (11, 'Noviembre'),
    (12, 'Diciembre'),
]

def _a_fecha_local(fecha):
    """Convierte la fecha a zona local cuando es posible, ignorando errores."""

    if not fecha:
        return None
    if timezone.is_aware(fecha):
        try:
            return timezone.localtime(fecha)
        except (ValueError, OSError):
            return fecha
    return fecha


def _generar_csv_citas(queryset, nombre_archivo):
    """Devuelve un CSV con el detalle de las citas del queryset proporcionado."""

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    writer = csv.writer(response)
    writer.writerow(
        [
            'N° Cita',
            'Fecha',
            'Estado',
            'Asistencia',
            'Servicio',
            'Profesional',
            'Cliente',
            'Mascota',
        ]
    )
    for cita in queryset:
        profesional = getattr(cita.usuario, 'get_full_name', lambda: str(cita.usuario))()
        if not profesional:
            profesional = getattr(cita.usuario, 'username', str(cita.usuario))
        fecha_local = _a_fecha_local(cita.fecha)
        fecha_texto = fecha_local.strftime('%Y-%m-%d %H:%M') if fecha_local else ''
        writer.writerow(
            [
                cita.n_cita,
                fecha_texto,
                cita.get_estado_display(),
                cita.get_asistencia_display(),
                cita.get_servicio_display(),
                profesional,
                getattr(cita.cliente, 'nombre_cliente', ''),
                getattr(cita.mascota, 'nombre', ''),
            ]
        )
    return response


def dashboard(request):
    """Vista de indicadores operativos para el panel del trabajador."""
    if not request.user.is_authenticated:
        return redirect('panel_home')

    if not request.user.has_perm('paneltrabajador.view_cita'):
        messages.error(request, "No tiene los permisos para realizar esto.")
        return redirect('panel_home')

    grupos_usuario = set(request.user.groups.values_list('name', flat=True))
    puede_ver_global = bool(grupos_usuario.intersection({'recepcionista', 'gerente'}))

    if puede_ver_global:
        citas_base = Cita.objects.all()
    else:
        citas_base = Cita.objects.filter(usuario=request.user)
    
    citas_base = citas_base.filter(fecha__isnull=False)

    now = timezone.localtime()
    fechas_locales = []
    for fecha in citas_base.values_list('fecha', flat=True):
        fecha_local = _a_fecha_local(fecha)
        if fecha_local:
            fechas_locales.append(fecha_local)

    meses_disponibles = sorted(
        {fecha.date().replace(day=1) for fecha in fechas_locales},
        reverse=True,
    )
    anios_disponibles = sorted({fecha.year for fecha in fechas_locales}, reverse=True)

    primer_anio = anios_disponibles[0] if anios_disponibles else None
    primer_mes = meses_disponibles[0] if meses_disponibles else None

    default_year = primer_anio if primer_anio else now.year
    default_month = primer_mes.month if primer_mes else now.month

    try:
        selected_year = int(request.GET.get('year', default_year))
    except (TypeError, ValueError):
        selected_year = default_year

    try:
        selected_month = int(request.GET.get('month', default_month))
    except (TypeError, ValueError):
        selected_month = default_month

    if selected_month < 1 or selected_month > 12:
        selected_month = default_month

    zona = timezone.get_current_timezone()
    inicio_mes_seleccionado = datetime(selected_year, selected_month, 1)
    if timezone.is_naive(inicio_mes_seleccionado):
        inicio_mes_seleccionado = timezone.make_aware(inicio_mes_seleccionado, zona)

    if selected_month == 12:
        fin_mes = datetime(selected_year + 1, 1, 1)
    else:
        fin_mes = datetime(selected_year, selected_month + 1, 1)
    if timezone.is_naive(fin_mes):
        fin_mes = timezone.make_aware(fin_mes, zona)

    citas_mes = citas_base.filter(fecha__gte=inicio_mes_seleccionado, fecha__lt=fin_mes)

    export_type = request.GET.get('export')
    if export_type in {'mes', 'anio'}:
        if export_type == 'mes':
            queryset_export = (
                citas_base.filter(fecha__gte=inicio_mes_seleccionado, fecha__lt=fin_mes)
                .select_related('cliente', 'mascota', 'usuario')
                .order_by('fecha')
            )
            nombre_archivo = f'dashboard_{selected_year}_{selected_month:02d}.csv'
        else:
            inicio_anio = datetime(selected_year, 1, 1)
            fin_anio = datetime(selected_year + 1, 1, 1)
            if timezone.is_naive(inicio_anio):
                inicio_anio = timezone.make_aware(inicio_anio, zona)
            if timezone.is_naive(fin_anio):
                fin_anio = timezone.make_aware(fin_anio, zona)
            queryset_export = (
                citas_base.filter(fecha__gte=inicio_anio, fecha__lt=fin_anio)
                .select_related('cliente', 'mascota', 'usuario')
                .order_by('fecha')
            )
            nombre_archivo = f'dashboard_{selected_year}_anual.csv'

        return _generar_csv_citas(queryset_export, nombre_archivo)

    total_reservadas_mes = citas_mes.filter(estado='1').count()
    total_canceladas_mes = citas_mes.filter(estado='2').count()
    total_no_tomadas_mes = citas_mes.filter(estado='3').count()
    total_asistencias_mes = citas_mes.filter(asistencia='A').count()
    total_pendientes_asistencia_mes = citas_mes.filter(asistencia='P').count()

    total_operativo_mes = total_reservadas_mes + total_canceladas_mes + total_no_tomadas_mes
    tasa_cancelacion_mes = 0.0
    if total_operativo_mes:
        tasa_cancelacion_mes = round((total_canceladas_mes / total_operativo_mes) * 100, 1)

    servicios_reservas = (
        citas_mes.filter(estado='1')
        .values('servicio')
        .annotate(total=Count('servicio'))
        .order_by('-total')
    )

    servicio_dict = dict(Cita.SERVICIO_CHOICES)
    servicios_reservas = [
        {
            'servicio': servicio_dict.get(item['servicio'], item['servicio']),
            'total': item['total'],
        }
        for item in servicios_reservas
    ]

    inicio_periodo = inicio_mes_seleccionado - timedelta(days=180)
    tendencias_registros = citas_base.filter(fecha__gte=inicio_periodo).values_list('fecha', 'estado')
    tendencias_acumulado = defaultdict(lambda: {'reservadas': 0, 'canceladas': 0})
    for fecha, estado in tendencias_registros:
        fecha_local = _a_fecha_local(fecha)
        if not fecha_local:
            continue
        periodo = fecha_local.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if estado == '1':
            tendencias_acumulado[periodo]['reservadas'] += 1
        elif estado == '2':
            tendencias_acumulado[periodo]['canceladas'] += 1

    tendencias_mensuales = [
        {
            'periodo': periodo.strftime('%b %Y'),
            'reservadas': datos['reservadas'],
            'canceladas': datos['canceladas'],
        }
        for periodo, datos in sorted(tendencias_acumulado.items())
    ]

    proximas_citas = (
        citas_base.filter(
            fecha__gte=now,
            fecha__lte=now + timedelta(days=7),
            estado='1',
        )
        .select_related('cliente', 'mascota')
        .order_by('fecha')[:10]
    )

    nombre_mes = dict(MESES_NOMBRES).get(selected_month, '')
    mes_actual_label = f"{nombre_mes} {selected_year}".strip()

    year_options = anios_disponibles or [default_year]
    month_options = [{'value': numero, 'label': nombre} for numero, nombre in MESES_NOMBRES]

    export_mes_url = f"{request.path}?" + urlencode(
        {'year': selected_year, 'month': selected_month, 'export': 'mes'}
    )
    export_anio_url = f"{request.path}?" + urlencode({'year': selected_year, 'export': 'anio'})

    contexto = {
        'alcance_global': puede_ver_global,
        'total_reservadas_mes': total_reservadas_mes,
        'total_canceladas_mes': total_canceladas_mes,
        'total_no_tomadas_mes': total_no_tomadas_mes,
        'total_asistencias_mes': total_asistencias_mes,
        'total_pendientes_asistencia_mes': total_pendientes_asistencia_mes,
        'tasa_cancelacion_mes': tasa_cancelacion_mes,
        'servicios_reservas': servicios_reservas,
        'tendencias_mensuales': tendencias_mensuales,
        'proximas_citas': proximas_citas,
        'mes_actual_label': mes_actual_label,
        'selected_year': selected_year,
        'selected_month': selected_month,
        'year_options': year_options,
        'month_options': month_options,
        'export_mes_url': export_mes_url,
        'export_anio_url': export_anio_url,
    }

    return render(request, 'paneltrabajador/dashboard.html', contexto)