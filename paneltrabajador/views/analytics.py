from collections import defaultdict
from datetime import timedelta

from django.contrib import messages
from django.db.models import Avg, Count, DurationField, ExpressionWrapper, F, Min, Q
from django.shortcuts import redirect, render
from django.utils import timezone
from django.db.models.functions import Cast, ExtractHour, TruncMonth
from django.db.models import DateField

from paneltrabajador.models import ChatConversation, ChatMessage, Cita, EvolucionClinica


def analytics_insights(request):
    """Panel de analítica y minería de datos operativa."""

    if not request.user.is_authenticated:
        return redirect("panel_home")

    if not request.user.has_perm("paneltrabajador.view_cita"):
        messages.error(request, "No tiene los permisos para realizar esto.")
        return redirect("panel_home")

    grupos_usuario = set(request.user.groups.values_list("name", flat=True))
    puede_ver_global = bool(grupos_usuario.intersection({"recepcionista", "gerente"}))

    citas_base = Cita.objects.filter(fecha__isnull=False)
    if not puede_ver_global:
        citas_base = citas_base.filter(usuario=request.user)

    ahora = timezone.localtime()
    inicio_90_dias = ahora - timedelta(days=90)
    inicio_180_dias = ahora - timedelta(days=180)

    citas_periodo = citas_base.filter(fecha__gte=inicio_90_dias)
    total_citas_periodo = citas_periodo.count()
    total_asistidas = citas_periodo.filter(asistencia="A").count()
    total_no_show = citas_periodo.filter(asistencia="N").count()
    total_canceladas = citas_periodo.filter(estado="2").count()
    total_reservadas = citas_periodo.filter(estado="1").count()

    tasa_asistencia = round((total_asistidas / total_citas_periodo) * 100, 1) if total_citas_periodo else 0
    tasa_no_show = round((total_no_show / total_citas_periodo) * 100, 1) if total_citas_periodo else 0
    tasa_cancelacion = round((total_canceladas / total_citas_periodo) * 100, 1) if total_citas_periodo else 0

    rendimiento_servicios = (
        citas_periodo
        .values("servicio")
        .annotate(
            total=Count("pk"),
            asistidas=Count("pk", filter=Q(asistencia="A")),
            no_show=Count("pk", filter=Q(asistencia="N")),
            canceladas=Count("pk", filter=Q(estado="2")),
        )
        .order_by("-total")
    )
    servicio_labels = dict(Cita.SERVICIO_CHOICES)
    servicios_resumen = [
        {
            "servicio": servicio_labels.get(item["servicio"], item["servicio"]),
            "total": item["total"],
            "asistidas": item["asistidas"],
            "no_show": item["no_show"],
            "canceladas": item["canceladas"],
        }
        for item in rendimiento_servicios
    ]

    clientes_recurrentes = (
        citas_base.filter(estado="1", fecha__gte=inicio_180_dias, cliente__isnull=False)
        .values("cliente__rut", "cliente__nombre_cliente")
        .annotate(total=Count("pk"))
        .order_by("-total", "cliente__nombre_cliente")[:5]
    )

    evoluciones_base = EvolucionClinica.objects.filter(creado_en__gte=inicio_180_dias)
    if not puede_ver_global:
        evoluciones_base = evoluciones_base.filter(cita__usuario=request.user)

    evoluciones_por_mes = (
        evoluciones_base
        .annotate(periodo=Cast(TruncMonth("creado_en"), output_field=DateField()))
        .values("periodo", "servicio")
        .annotate(total=Count("pk"))
        .order_by("periodo")
    )
    evoluciones_series = defaultdict(list)
    for item in evoluciones_por_mes:
        periodo = item["periodo"]
        label = periodo.strftime("%b %Y") if periodo else ""
        evoluciones_series[label].append(
            {
                "servicio": servicio_labels.get(item["servicio"], item["servicio"]),
                "total": item["total"],
            }
        )


    chat_conversaciones = ChatConversation.objects.filter(created_at__gte=inicio_90_dias)
    if not puede_ver_global:
        chat_conversaciones = chat_conversaciones.filter(assigned_to=request.user)
    chat_totales = chat_conversaciones.aggregate(
        pendientes=Count("pk", filter=Q(state=ChatConversation.STATE_PENDING)),
        activas=Count("pk", filter=Q(state=ChatConversation.STATE_ACTIVE)),
        cerradas=Count("pk", filter=Q(state=ChatConversation.STATE_CLOSED)),
        total=Count("pk"),
    )

    with_respuesta = chat_conversaciones.annotate(
        primera_respuesta=Min(
            "messages__created_at",
            filter=Q(messages__author=ChatMessage.AUTHOR_STAFF),
        )
    ).annotate(
        demora_respuesta=ExpressionWrapper(
            F("primera_respuesta") - F("created_at"),
            output_field=DurationField(),
        )
    )

    metrica_respuesta = with_respuesta.aggregate(
        conversaciones_contestadas=Count("pk", filter=Q(primera_respuesta__isnull=False)),
        demora_promedio=Avg("demora_respuesta"),
    )

     # --- Minería ligera: estimación de riesgo de no-show para las próximas citas ---
    historial_modelo = citas_base.filter(
        fecha__lt=ahora, fecha__gte=inicio_180_dias, asistencia__in=["A", "N"]
    )
    total_historial = historial_modelo.count()
    base_no_show = (
        historial_modelo.filter(asistencia="N").count() / total_historial
        if total_historial
        else 0
    )

    servicio_no_show = {
        item["servicio"]: item["no_show"] / item["total"]
        for item in historial_modelo.values("servicio")
        .annotate(
            total=Count("pk"),
            no_show=Count("pk", filter=Q(asistencia="N")),
        )
        .filter(total__gte=5)
    }

    hora_no_show = {}
    hora_stats = (
        historial_modelo.annotate(hora=ExtractHour("fecha"))
        .values("hora")
        .annotate(total=Count("pk"), no_show=Count("pk", filter=Q(asistencia="N")))
    )
    for stat in hora_stats:
        hora = stat["hora"]
        if stat["total"] >= 5 and hora is not None:
            hora_no_show[int(hora)] = stat["no_show"] / stat["total"]

    def riesgo_no_show(cita):
        if not total_historial:
            return 0, ["Sin suficientes datos históricos"]

        explicaciones = ["Tasa base calculada con los últimos 6 meses"]
        servicio_rate = servicio_no_show.get(cita.servicio, base_no_show)
        hora_local = timezone.localtime(cita.fecha).hour
        hora_rate = hora_no_show.get(hora_local, base_no_show)

        puntaje = (base_no_show * 0.4) + (servicio_rate * 0.35) + (hora_rate * 0.25)

        if servicio_rate != base_no_show:
            explicaciones.append(
                f"Servicio con tasa histórica de no-show del {round(servicio_rate * 100, 1)}%"
            )
        if hora_rate != base_no_show:
            explicaciones.append(
                f"Horario con tasa histórica del {round(hora_rate * 100, 1)}%"
            )

        return round(puntaje * 100, 1), explicaciones

    proximas_citas = (
        citas_base.filter(estado="1", fecha__gte=ahora)
        .order_by("fecha")[:8]
    )
    proximas_con_riesgo = []
    servicio_labels = dict(Cita.SERVICIO_CHOICES)
    for cita in proximas_citas:
        probabilidad, explicaciones = riesgo_no_show(cita)
        nivel = (
            "Alto" if probabilidad >= 40 else "Medio" if probabilidad >= 20 else "Bajo"
        )
        proximas_con_riesgo.append(
            {
                "cita": cita,
                "probabilidad": probabilidad,
                "nivel": nivel,
                "servicio": servicio_labels.get(cita.servicio, cita.servicio),
                "explicaciones": explicaciones,
            }
        )

    contexto = {
        "alcance_global": puede_ver_global,
        "total_citas_periodo": total_citas_periodo,
        "total_asistidas": total_asistidas,
        "total_no_show": total_no_show,
        "total_canceladas": total_canceladas,
        "total_reservadas": total_reservadas,
        "tasa_asistencia": tasa_asistencia,
        "tasa_no_show": tasa_no_show,
        "tasa_cancelacion": tasa_cancelacion,
        "servicios_resumen": servicios_resumen,
        "clientes_recurrentes": clientes_recurrentes,
        "evoluciones_series": dict(evoluciones_series),
        "chat_totales": chat_totales,
        "metrica_respuesta": metrica_respuesta,
        "fecha_desde": inicio_90_dias.date(),
        "fecha_desde_larga": inicio_180_dias.date(),
        "proximas_con_riesgo": proximas_con_riesgo,
        "base_no_show": round(base_no_show * 100, 1),
    }

    return render(request, "paneltrabajador/analytics.html", contexto)