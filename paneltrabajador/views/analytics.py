from collections import defaultdict
from datetime import timedelta

from django.contrib import messages
from django.db.models import Avg, Count, DurationField, ExpressionWrapper, F, Min, Q
from django.shortcuts import redirect, render
from django.utils import timezone
from django.db.models.functions import TruncMonth, Cast
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
    }

    return render(request, "paneltrabajador/analytics.html", contexto)