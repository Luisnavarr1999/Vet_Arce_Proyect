from ast import And
from urllib import request
from datetime import datetime, time, timedelta
from typing import Optional
from django.shortcuts import redirect, render
from django.urls import reverse
from django.template import loader
from django import forms
from django.contrib import messages
from ambpublica.forms import (
    ContactForm,
    BuscarMascotaForm,
    CancelarCitaForm,
    CitaForm,
    MascotaSelectForm,
    RutForm,
    ServicioForm,
)

from paneltrabajador.forms import ClienteForm, MascotaForm
from paneltrabajador.models import Cita, Cliente, Mascota, ChatConversation, ChatMessage

import json
from django.http import Http404, HttpResponse, JsonResponse
import logging
from django.core.cache import cache
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.formats import date_format
from django.core.mail import EmailMultiAlternatives
from django.db.models import Count

from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST
import random
import re, unicodedata

# Create your views here.

# Renderiza la página principal
@ensure_csrf_cookie
def main(request):
    contact_success = False
    contact_error = None

    if request.method == 'POST':
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            data = contact_form.cleaned_data
            subject = f"Consulta desde la web - {data['nombre']}"
            message_body = (
                "Se ha recibido un nuevo mensaje desde la página principal.\n\n"
                f"Nombre: {data['nombre']}\n"
                f"Correo: {data['correo']}\n"
                f"Fecha: {timezone.localtime(timezone.now()).strftime('%d-%m-%Y %H:%M')}\n\n"
                "Mensaje:\n"
                f"{data['mensaje']}"
            )

            try:
                send_mail(
                    subject,
                    message_body,
                    settings.DEFAULT_FROM_EMAIL,
                    [getattr(settings, 'CONTACT_EMAIL', settings.DEFAULT_FROM_EMAIL)],
                    fail_silently=False,
                )
            except Exception as exc:
                contact_error = (
                    'Ocurrió un problema al enviar tu mensaje. Por favor, inténtalo nuevamente más tarde.'
                )
                logger.exception('Error enviando mensaje de contacto: %s', exc)
            else:
                contact_success = True
                contact_form = ContactForm()
        else:
            contact_error = None
    else:
        contact_form = ContactForm()

    context = {
        'contact_form': contact_form,
        'contact_success': contact_success,
        'contact_error': contact_error,
        'chatbot_conversation_id': request.session.get(ACTIVE_CONVERSATION_KEY),
    }

    return render(request, 'ambpublica/main.html', context)

# cosas que responde el chat demo

def _normalize(txt: str) -> str:
    # minúsculas + sin acentos
    txt = txt.lower()
    txt = unicodedata.normalize("NFD", txt)
    return "".join(c for c in txt if unicodedata.category(c) != "Mn")

# Cada intent tiene un patrón regex y un set de respuestas posibles
INTENTS = [
    # Saludo / Despedida
    (re.compile(r"^(ola|hola|buenas|buenos dias|buenas tardes|buenas noches|oña)\b"), (
        "¡Hola! 😊 Soy el asistente virtual de la Veterinaria de Arce. ¿En qué te puedo apoyar hoy?",
        "¡Hola hola! 👋 Estoy aquí para ayudarte con horarios, servicios o tus reservas.",
        "¡Bienvenido! Soy el asistente de la Veterinaria de Arce. Cuéntame, ¿qué necesitas?",
    )),
    (re.compile(r"\b(gracias|chau|adios|adiós|nos vemos)\b"), (
        "¡Gracias por escribirnos! 🐾 Si necesitas algo más, aquí estoy.",
        "¡Un gusto ayudarte! Que tengas un excelente día.",
        "¡Hasta luego! Dale muchos cariños a tu peludo de nuestra parte.",
    )),

    # Horarios
    (re.compile(r"\b(horario|horarios|abren|cierran|apertura|cierre)\b"), (
        "Atendemos de lunes a viernes 09:00–19:00 y los sábados de 10:00–14:00 🕘",
        "Nuestro horario es lunes a viernes de 09:00 a 19:00, sábados hasta las 14:00.",
        "Abrimos de 9 a 19 h en semana y los sábados de 10 a 14 h. ¡Te esperamos!",
    )),

    # Ubicación
    (re.compile(r"\b(ubicacion|ubicación|direccion|dirección|donde|dónde|como llegar)\b"), (
        "Estamos en Santiago Centro. En la sección Contacto tienes el mapa exacto 📍",
        "Nos encuentras en pleno Santiago Centro; en Contacto puedes abrir el mapa y trazarte la ruta.",
        "Nuestra clínica está en Santiago Centro, con fácil acceso. ¿Necesitas que te enviemos el mapa?",
    )),

    # Contacto
    (re.compile(r"\b(contacto|telefono|teléfono|whatsapp|correo|email)\b"), (
        "Puedes escribirnos por aquí, llamar a recepción o enviarnos un correo y te respondemos rápido.",
        "Además del chat, atendemos por teléfono y correo. ¡Elige el canal que más te acomode!",
    )),

    # Servicios y precios
    (re.compile(r"\b(servicio|servicios|vacuna|vacunas|cirugia|cirugía|dentista|odontologia|peluquer|baño|desparasita)\b"), (
        "Ofrecemos consulta general, vacunas, odontología y cirugías. ¿Qué servicio te interesa?",
        "Tenemos consulta médica, procedimientos dentales, cirugías y planes preventivos. ¿Buscabas alguno en particular?",
    )),
    (re.compile(r"\b(precio|precios|cuanto cuesta|tarifa|valen)\b"), (
        "Los precios varían según el servicio y la mascota. Te puedo orientar por aquí y confirmar en recepción 💳",
        "Dependiendo del servicio cambia el valor. Cuéntame qué necesitas y te doy el rango referencial.",
    )),

    # Pagos
    (re.compile(r"\b(pago|pagos|tarjeta|efectivo|transfer|transferencia|webpay|promocion|promoción)\b"), (
        "Aceptamos tarjeta, transferencia y efectivo. Pregunta en recepción por promociones 💳",
        "Puedes pagar con tarjetas, transferencia o efectivo. Si necesitas boleta o factura, la emitimos al momento.",
    )),

    # Reservas / Cancelaciones
    (re.compile(r"\b(reserv(ar|a)|agendar|sacar hora|cita nueva)\b"), (
        "Puedes reservar desde “Reserva de Horas Online”. Si quieres, te voy guiando paso a paso 👍",
        "Te ayudo desde aquí y también puedes completar la reserva en la sección Reserva de Horas.",
    )),
    (re.compile(r"\b(cancelar (cita|hora)|anular (cita|hora)|reagendar|cambiar hora)\b"), (
        "Para cancelar o reagendar, indícanos tu número de cita o contáctanos por recepción.",
        "Si necesitas mover tu cita, con gusto te ayudamos; solo cuéntame el número o escríbenos a recepción.",
    )),

    # Emergencias
    (re.compile(r"\b(emergencia|emergencias|urgencia|urgencias|fuera de horario)\b"), (
        "Para emergencias fuera de horario, llámanos y coordinamos ayuda 📞",
        "En caso de urgencia contáctanos de inmediato por teléfono para coordinar la atención.",
    )),

    # Políticas / tiempos / requisitos
    (re.compile(r"\b(politica|política|no show|atraso|tarde|cancelacion|cancelación)\b"), (
        "Si no puedes asistir, avísanos con anticipación para liberar el cupo. ¡Gracias! 🙏",
        "Agradecemos que nos avises si te retrasas o debes cancelar, así ayudamos a otra mascota.",
    )),
    (re.compile(r"\b(tiempo|demora|cola|espera|cuanto se demoran)\b"), (
        "El tiempo de atención depende del día y la demanda. ¡Hacemos lo posible por atender rápido!",
        "Los tiempos pueden variar según la carga del día, pero siempre intentamos agilizar la espera.",
    )),
    (re.compile(r"\b(requisito|requisitos|primera consulta|documento|documentos)\b"), (
        "Trae el RUT del tutor y, si tienes, el historial o carnet de tu mascota.",
        "Con el RUT del tutor y el historial médico (si lo tienes) es suficiente para partir.",
    )),
    
    # Otros comunes
    (re.compile(r"\b(estacionamiento|parking)\b"), (
        "Tenemos estacionamiento cercano con convenios en ciertos horarios.",
        "Podemos indicarte estacionamientos aliados a pocos metros si lo necesitas.",
    )),
    (re.compile(r"\b(exotica|exótica|aves|reptil|reptiles|huron|hurón)\b"), (
        "Atendemos mascotas comunes. Para exóticos, consúltanos caso a caso.",
        "Para especies exóticas analizamos cada caso; cuéntame qué necesitas y vemos disponibilidad.",
    )),
    (re.compile(r"\b(domicilio|a domicilio|visita a domicilio)\b"), (
        "Podemos coordinar visitas a domicilio en zonas cercanas. Escríbenos para evaluar.",
        "En algunos sectores realizamos visitas a domicilio; conversemos los detalles y vemos factibilidad.",
    )),
]

FALLBACK_REPLIES = (
    "No estoy seguro de cómo ayudarte con eso. ¿Quieres que te contacte una recepcionista humana? Responde “sí” o “no”.",
    "Mmm, esa pregunta me queda grande. Si quieres hablo con recepción para que te apoyen; dime “sí” o “no”.",
)

def _pick_reply(reply_options):
    if isinstance(reply_options, (list, tuple)):
        return random.choice(reply_options)
    return reply_options

def _rule_based_answer(message: str) -> tuple[str, bool]:
    q = _normalize(message)
    for pattern, reply in INTENTS:
        if pattern.search(q):
            return _pick_reply(reply), False
    # fallback
    return _pick_reply(FALLBACK_REPLIES), True

def _find_chatbot_answer(message: str):
    return _rule_based_answer(message)

logger = logging.getLogger(__name__)

SERVICE_HIGHLIGHTS = {
    'general': {
        'icon': 'bi-heart-pulse',
        'description': 'Controles, chequeos preventivos y orientación integral para la salud de tu mascota.',
    },
    'cirugia': {
        'icon': 'bi-hospital',
        'description': 'Procedimientos quirúrgicos programados con seguimiento posoperatorio especializado.',
    },
    'dentista': {
        'icon': 'bi-tooth',
        'description': 'Limpiezas dentales y tratamientos para mantener la salud bucal de tu compañero.',
    },
}

RESERVA_PROGRESS = [
    {'label': 'Servicio', 'icon': 'bi-list-check', 'steps': {'', 'nohours'}},
    {'label': 'Datos del tutor', 'icon': 'bi-person-badge', 'steps': {'ingresar_rut', 'crear_cliente'}},
    {'label': 'Mascota', 'icon': 'bi-bag-heart', 'steps': {'select_mascota', 'crear_mascota'}},
    {'label': 'Confirmación', 'icon': 'bi-check2-circle', 'steps': {'final'}},
]


def _build_service_highlights(codes=None):
    """Regresa información enriquecida de servicios disponibles."""

    choices = dict(Cita.SERVICIO_CHOICES)
    if codes is None:
        codes = [value for value, _ in Cita.SERVICIO_CHOICES]

    highlights = []
    for code in codes:
        data = SERVICE_HIGHLIGHTS.get(code, {})
        highlights.append({
            'code': code,
            'name': choices.get(code, code.title()),
            'description': data.get('description', ''),
            'icon': data.get('icon', 'bi-calendar-heart'),
        })
    return highlights


def _get_progress_state(step):
    """Construye el estado visual del progreso del flujo de reserva."""

    current_index = 0
    success_mode = False
    for idx, stage in enumerate(RESERVA_PROGRESS):
        if step in stage['steps']:
            current_index = idx
            break
    else:
        if step == 'success':
            current_index = len(RESERVA_PROGRESS)
            success_mode = True

    progress = []
    for idx, stage in enumerate(RESERVA_PROGRESS):
        progress.append({
            'label': stage['label'],
            'icon': stage['icon'],
            'is_current': idx == current_index and not success_mode,
            'is_completed': idx < current_index if not success_mode else True,
        })
    return progress


def _build_confirmation_payload(cita, *, cliente=None, mascota=None):
    """Crea la información necesaria para renderizar la página de confirmación."""

    cliente = cliente or cita.cliente
    mascota = mascota or cita.mascota

    fecha_local = timezone.localtime(cita.fecha)
    servicio_str = dict(Cita.SERVICIO_CHOICES).get(cita.servicio, cita.servicio)
    veterinario_nombre = cita.usuario.get_full_name().strip() or cita.usuario.get_username()

    return {
        'cliente': {
            'nombre': getattr(cliente, 'nombre_cliente', ''),
            'rut': getattr(cliente, 'rut', ''),
            'telefono': getattr(cliente, 'telefono', ''),
            'email': getattr(cliente, 'email', ''),
            'direccion': getattr(cliente, 'direccion', ''),
        },
        'mascota': {
            'nombre': getattr(mascota, 'nombre', ''),
            'numero_chip': getattr(mascota, 'numero_chip', ''),
        },
        'fecha': fecha_local.strftime('%d-%m-%Y'),
        'hora': fecha_local.strftime('%H:%M'),
        'veterinario': veterinario_nombre,
        'servicio': servicio_str,
        'numero_cita': cita.n_cita,
    }

MAX_MSG_LEN = 500          # Máximo ancho de mensaje aceptado
RATE_LIMIT_WINDOW = 30     # Ventana en segundos
RATE_LIMIT_MAX = 15        # Máximo de mensajes por ventana e IP

HANDOFF_PENDING_KEY = "chatbot_pending_handoff"
HANDOFF_MESSAGE_KEY = "chatbot_pending_message"
ACTIVE_CONVERSATION_KEY = "chatbot_conversation_id"

SERVICIOS_INFO = {
    "consulta-general": {
        "slug": "consulta-general",
        "name": "Consulta General",
        "tagline": "Salud preventiva y acompañamiento médico para cada etapa de vida.",
        "description": (
            "Durante la consulta general evaluamos el estado integral de tu mascota, "
            "incluyendo antecedentes médicos, chequeos físicos completos y un plan de cuidado a medida."
        ),
        "services": [
            "Evaluación clínica completa con control de signos vitales",
            "Calendario de vacunación y desparasitación actualizado",
            "Asesoría nutricional y de comportamiento",
            "Exámenes preventivos según edad y especie",
        ],
        "benefits": [
            "Detección temprana de enfermedades y condiciones crónicas",
            "Planes de salud personalizados que se adaptan a tu rutina",
            "Registro clínico digital disponible en todo momento",
            "Recomendaciones para mejorar su calidad de vida diaria",
        ],
        "tips": [
            "Trae el carnet sanitario o antecedentes médicos para una evaluación más completa.",
            "Anota dudas o cambios recientes en su comportamiento para comentarlos durante la visita.",
            "Mantén su calendario de vacunas al día para prevenir enfermedades comunes.",
        ],
        "hero_image": "Imagenes/servicios/consulta-general-hero.jpg",
        "gallery_images": [
            {"src": "Imagenes/servicios/consulta-general-1.jpg", "alt": "Veterinaria revisando a un perro"},
            {"src": "Imagenes/servicios/consulta-general-2.jpg", "alt": "Chequeo de gato en consulta"},
        ],
    },
    "cirugia": {
        "slug": "cirugia",
        "name": "Cirugía Veterinaria",
        "tagline": "Procedimientos seguros con tecnología y monitoreo de última generación.",
        "description": (
            "Nuestro equipo quirúrgico combina experiencia, protocolos estrictos de bioseguridad y equipos "
            "de monitoreo avanzados para ofrecer cirugías seguras y una recuperación tranquila."
        ),
        "services": [
            "Cirugías programadas y de urgencia para tejidos blandos",
            "Esterilizaciones y castraciones con protocolos modernos",
            "Monitoreo anestésico continuo por personal especializado",
            "Hospitalización postoperatoria con controles periódicos",
        ],
        "benefits": [
            "Evaluación preoperatoria integral para minimizar riesgos",
            "Acompañamiento cercano durante todo el proceso de recuperación",
            "Planes de manejo del dolor adaptados a cada paciente",
            "Comunicación constante y reportes de evolución a la familia",
        ],
        "tips": [
            "Sigue las indicaciones de ayuno y medicamentos antes de la cirugía.",
            "Prepara un espacio tranquilo en casa para el reposo postoperatorio.",
            "Acude a los controles programados para asegurar una recuperación óptima.",
        ],
        "hero_image": "Imagenes/servicios/cirugia-hero.jpg",
        "gallery_images": [
            {"src": "Imagenes/servicios/cirugia-1.jpg", "alt": "Equipo veterinario en pabellón"},
            {"src": "Imagenes/servicios/cirugia-2.jpg", "alt": "Mascota descansando tras cirugía"},
        ],
    },
    "dentista": {
        "slug": "dentista",
        "name": "Odontología Veterinaria",
        "tagline": "Sonrisas sanas para mejorar la salud general de tu compañero.",
        "description": (
            "El cuidado dental es esencial para prevenir infecciones y molestias. En nuestra área odontológica "
            "trabajamos con equipos especializados y técnicas delicadas para proteger la salud bucal."
        ),
        "services": [
            "Limpieza dental con ultrasonido y pulido profesional",
            "Extracciones seguras y tratamientos periodontales",
            "Diagnóstico por imagen para evaluar raíces y maxilares",
            "Plan de cuidado dental domiciliario con productos recomendados",
        ],
        "benefits": [
            "Prevención de halitosis y enfermedades periodontales",
            "Mayor bienestar general y apetito equilibrado",
            "Seguimiento personalizado según especie y edad",
            "Educación al tutor para mantener una higiene diaria efectiva",
        ],
        "tips": [
            "Introduce el cepillado dental de manera gradual y positiva.",
            "Utiliza snacks y juguetes dentales aprobados por el veterinario.",
            "Programa limpiezas profesionales regulares para evitar acumulación de placa.",
        ],
        "hero_image": "Imagenes/servicios/dentista-hero.jpg",
        "gallery_images": [
            {"src": "Imagenes/servicios/dentista-1.jpg", "alt": "Dentista veterinario limpiando dientes a un perro"},
            {"src": "Imagenes/servicios/dentista-2.jpg", "alt": "Gato mostrando dientes sanos"},
        ],
    },
}

YES_KEYWORDS = {
    "si",
    "claro",
    "afirmativo",
    "ok",
    "okay",
    "dale",
    "porfavor",
    "porfa",
}
YES_PHRASES = (
    "quiero hablar",
    "quiero comunicarme",
    "hablar con la recepcion",
    "hablar con recepcion",
    "hablar con una recepcionista",
)
NO_KEYWORDS = {"no", "nop", "negativo"}
NO_PHRASES = ("no gracias", "prefiero seguir", "mejor no")

APPOINTMENT_LOOKUP_STATE_KEY = "chatbot_lookup_state"
AVAILABILITY_STATE_KEY = "chatbot_availability_state"
APPOINTMENT_LOOKUP_RECENT_DAYS = 7
FLOW_CANCEL_KEYWORDS = {"cancelar", "cancela", "olvida", "no importa", "gracias igual"}

APPOINTMENT_PATTERNS = [
    re.compile(r"\b(tengo|tenemos) (una )?(cita|hora)\b"),
    re.compile(r"\b(citas?|horas?) (agendad[ao]s?|reservad[ao]s?)\b"),
    re.compile(r"\b(agende|reserve|agendamos|reservamos)\b.*\b(cita|hora)\b"),
]

APPOINTMENT_PROMPTS = {
    "ask_rut": (
        "¡Claro! Para revisar tus citas necesito el RUT del tutor (solo números, sin puntos ni guion).",
        "Con gusto, primero dime el RUT del tutor, por favor (ej: 12345678).",
    ),
    "ask_rut_again": (
        "No logré reconocer el RUT. ¿Puedes enviarlo en formato 12345678, sin puntos ni dígito verificador?",
        "Creo que hubo un error con el RUT. Inténtalo nuevamente solo con números, porfa.",
    ),
    "ask_pet": (
        "Gracias. ¿Cómo se llama la mascota que quieres revisar?",
        "Perfecto, ahora dime el nombre de tu mascota para buscar sus citas.",
    ),
    "ask_pet_again": (
        "No alcancé a captar el nombre. ¿Me lo repites?",
        "Necesito el nombre de la mascota tal como la registraste. ¿Cuál es?",
    ),
    "client_missing": (
        "No encuentro un tutor con ese RUT en nuestros registros. ¿Lo revisamos nuevamente?",
        "No ubico ese RUT en la base. ¿Podrías confirmarlo o intentar con otro?",
    ),
    "pet_missing": (
        "No encuentro esa mascota asociada al RUT entregado. ¿Podrías decirme otro nombre o revisar si está bien escrito?",
        "No veo ese nombre en la ficha del tutor. ¿Quizá usaste otro diminutivo al registrarla?",
    ),
    "cancel": (
        "Sin problema, cuando quieras retomamos la búsqueda de citas.",
        "Listo, dejamos en pausa la consulta. Si necesitas otra cosa me avisas.",
    ),
}

AVAILABILITY_KEYWORDS = (
    "disponibilidad",
    "disponible",
    "horas",
    "horario",
    "horarios",
    "cupo",
    "cupos",
    "agenda",
    "reservar",
    "agendar",
)

AVAILABILITY_PROMPTS = {
    "ask_date": (
        "¿Para qué día quieres revisar disponibilidad?", 
        "Encantado. ¿Qué día tienes en mente para revisar si hay cupos?",
    ),
    "cancel": (
        "Sin problema, dime cuando quieras revisar otra fecha.",
    ),
}

WEEKDAY_MAP = {
    "lunes": 0,
    "martes": 1,
    "miercoles": 2,
    "miércoles": 2,
    "jueves": 3,
    "viernes": 4,
    "sabado": 5,
    "sábado": 5,
    "domingo": 6,
}

WEEKDAY_DISPLAY = {
    0: "lunes",
    1: "martes",
    2: "miércoles",
    3: "jueves",
    4: "viernes",
    5: "sábado",
    6: "domingo",
}

SERVICE_KEYWORDS = {
    "general": ("general", "control", "consulta"),
    "cirugia": ("cirugia", "cirugía", "operacion", "operación"),
    "dentista": ("dentista", "dental", "odontologia", "odontología"),
}

DATE_PATTERN = re.compile(r"(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?")


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"\b\w+\b", text))

def servicio_detalle(request, slug: str):
    servicio = SERVICIOS_INFO.get(slug)
    if not servicio:
        raise Http404("Servicio no encontrado")

    context = {
        "servicio": servicio,
    }

    return render(request, "ambpublica/servicio_detalle.html", context)


def _should_escalate(normalized_message: str) -> Optional[bool]:
    tokens = _tokenize(normalized_message)
    if tokens & YES_KEYWORDS:
        return True
    for phrase in YES_PHRASES:
        if phrase in normalized_message:
            return True
    if tokens & NO_KEYWORDS:
        return False
    for phrase in NO_PHRASES:
        if phrase in normalized_message:
            return False
    return None

def _contains_negative_intent(normalized_message: str) -> bool:
    tokens = _tokenize(normalized_message)
    if tokens & NO_KEYWORDS:
        return True
    for phrase in NO_PHRASES:
        if phrase in normalized_message:
            return True
    return False

def _clear_session_state(session, key: str):
    if key in session:
        session.pop(key, None)
        session.modified = True


def _format_rut_display(value: int) -> str:
    digits = f"{value:d}"
    parts = []
    while digits:
        parts.append(digits[-3:])
        digits = digits[:-3]
    return ".".join(reversed(parts))


def _extract_rut(text: str) -> Optional[int]:
    match = re.search(r"\b(\d{6,9})\b", text)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    return None


def _next_weekday(start_date, target_weekday: int):
    days_ahead = (target_weekday - start_date.weekday()) % 7
    return start_date + timedelta(days=days_ahead)


def _parse_requested_date(normalized_message: str):
    today = timezone.localdate()
    if "pasado manana" in normalized_message:
        return today + timedelta(days=2)
    if "manana" in normalized_message:
        return today + timedelta(days=1)
    if "hoy" in normalized_message:
        return today

    for word, weekday in WEEKDAY_MAP.items():
        if re.search(fr"\b{word}\b", normalized_message):
            return _next_weekday(today, weekday)

    match = DATE_PATTERN.search(normalized_message)
    if match:
        day, month, year = match.groups()
        try:
            day = int(day)
            month = int(month)
            year = int(year) if year else today.year
            if year < 100:
                year += 2000
            candidate = datetime(year, month, day).date()
        except ValueError:
            return None
        if candidate < today:
            try:
                candidate = datetime(year + 1, month, day).date()
            except ValueError:
                return None
        return candidate

    return None


def _detect_service_code(normalized_message: str) -> Optional[str]:
    for code, keywords in SERVICE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in normalized_message:
                return code
    return None


def _human_join(items: list[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + f" y {items[-1]}"


def _build_availability_reply(target_date, service_code: Optional[str]) -> str:
    start_dt = datetime.combine(target_date, time.min)
    end_dt = datetime.combine(target_date, time.max)
    if getattr(settings, "USE_TZ", False):
        tz = timezone.get_current_timezone()
        start_dt = timezone.make_aware(start_dt, tz)
        end_dt = timezone.make_aware(end_dt, tz)

    citas = Cita.objects.filter(estado='0', fecha__range=(start_dt, end_dt))
    service_labels = dict(Cita.SERVICIO_CHOICES)
    if service_code:
        citas = citas.filter(servicio=service_code)

    count = citas.count()
    weekday_label = WEEKDAY_DISPLAY.get(target_date.weekday(), target_date.strftime('%A')).capitalize()
    date_str = target_date.strftime('%d-%m-%Y')
    service_name = service_labels.get(service_code, None) if service_code else None
    service_fragment = f" para {service_name}" if service_name else ""

    if service_code:
        if count:
            options = (
                f"Para {weekday_label} {date_str} contamos con {count} horario(s){service_fragment} disponible(s). Puedes reservar desde la sección Reserva de Horas.",
                f"¡Buenas noticias! El {weekday_label} {date_str} todavía tenemos {count} cupo(s){service_fragment}. Puedes hacer la reserva online cuando quieras.",
            )
        else:
            options = (
                f"Ese {weekday_label} {date_str} ya no tiene cupos{service_fragment}. ¿Quieres que revisemos otro día?",
                f"Por ahora no tenemos disponibilidad{service_fragment} el {weekday_label} {date_str}. Quizá otra fecha te sirve, ¿te parece si la buscamos?",
            )
        return _pick_reply(options)

    per_service = list(
        citas.values('servicio')
        .annotate(total=Count('pk'))
        .order_by()
    )
    available_services = [
        f"{service_labels.get(row['servicio'], row['servicio'])} ({row['total']})"
        for row in per_service
        if row['total'] > 0
    ]

    if available_services:
        service_sentence = _human_join(available_services)
        options = (
            f"El {weekday_label} {date_str} tenemos cupos disponibles en {service_sentence}. Puedes reservar desde la sección Reserva de Horas.",
            f"Disponemos de cupos para {service_sentence} el {weekday_label} {date_str}. Si quieres, completa la reserva online cuando gustes.",
        )
    else:
        options = (
            f"Ese {weekday_label} {date_str} ya no tiene cupos disponibles. ¿Quieres que revisemos otro servicio o fecha?",
            f"Por ahora no tenemos disponibilidad en ningún servicio el {weekday_label} {date_str}. Podemos intentar con otra fecha si te acomoda.",
        )

    return _pick_reply(options)


def _lookup_cita_response(cliente: Cliente, mascota: Mascota):
    now = timezone.now()
    recent_cutoff = now - timedelta(days=APPOINTMENT_LOOKUP_RECENT_DAYS)

    citas = Cita.objects.filter(cliente=cliente, mascota=mascota).order_by('fecha')
    upcoming = citas.filter(fecha__gte=now, estado='1').first()
    recent = citas.filter(fecha__lt=now, fecha__gte=recent_cutoff, estado='1').order_by('-fecha').first()

    service_labels = dict(Cita.SERVICIO_CHOICES)

    if upcoming:
        fecha_local = timezone.localtime(upcoming.fecha)
        servicio = service_labels.get(upcoming.servicio, upcoming.servicio)
        return _pick_reply((
            f"Tienes una {servicio} agendada para {fecha_local.strftime('%d-%m-%Y a las %H:%M')}.",
            f"{mascota.nombre} tiene hora reservada el {fecha_local.strftime('%d-%m-%Y a las %H:%M')} para {servicio}.",
        ))

    if recent:
        fecha_local = timezone.localtime(recent.fecha)
        servicio = service_labels.get(recent.servicio, recent.servicio)
        return _pick_reply((
            f"No hay horas próximas, pero asistieron a {servicio} el {fecha_local.strftime('%d-%m-%Y a las %H:%M')}.",
            f"La última cita registrada fue el {fecha_local.strftime('%d-%m-%Y a las %H:%M')} ({servicio}). Si necesitas agendar otra, puedo orientarte.",
        ))

    return _pick_reply((
        f"Por ahora no registramos citas recientes ni próximas para {mascota.nombre}. ¿Quieres que revisemos disponibilidad?",
        f"No encuentro horas agendadas para {mascota.nombre} en estos días. Si quieres agendar una nueva, te acompaño en el proceso.",
    ))


def _handle_appointment_lookup(session, message: str, normalized_message: str):
    state = session.get(APPOINTMENT_LOOKUP_STATE_KEY)
    if state is not None and not isinstance(state, dict):
        _clear_session_state(session, APPOINTMENT_LOOKUP_STATE_KEY)
        state = None

    triggered = bool(state)
    if not triggered:
        triggered = any(pattern.search(normalized_message) for pattern in APPOINTMENT_PATTERNS)

    if not triggered:
        return None

    wants_cancel = any(word in normalized_message for word in FLOW_CANCEL_KEYWORDS)
    if not wants_cancel and state:
        wants_cancel = _contains_negative_intent(normalized_message)
    if wants_cancel:
        _clear_session_state(session, APPOINTMENT_LOOKUP_STATE_KEY)
        return {"reply": _pick_reply(APPOINTMENT_PROMPTS["cancel"])}

    if not state:
        rut_candidate = _extract_rut(normalized_message)
        state = {
            "rut": rut_candidate,
            "rut_display": _format_rut_display(rut_candidate) if rut_candidate else None,
            "pet_name": None,
            "pet_display": None,
        }
        session[APPOINTMENT_LOOKUP_STATE_KEY] = state
        session.modified = True
        if rut_candidate:
            return {"reply": _pick_reply(APPOINTMENT_PROMPTS["ask_pet"])}
        return {"reply": _pick_reply(APPOINTMENT_PROMPTS["ask_rut"])}

    if not state.get("rut"):
        rut_candidate = _extract_rut(normalized_message)
        if rut_candidate:
            state["rut"] = rut_candidate
            state["rut_display"] = _format_rut_display(rut_candidate)
            session[APPOINTMENT_LOOKUP_STATE_KEY] = state
            session.modified = True
            return {"reply": _pick_reply(APPOINTMENT_PROMPTS["ask_pet"])}
        return {"reply": _pick_reply(APPOINTMENT_PROMPTS["ask_rut_again"])}

    if not state.get("pet_name"):
        pet_name = re.sub(r"\s+", " ", message.strip())
        if len(pet_name) < 2:
            return {"reply": _pick_reply(APPOINTMENT_PROMPTS["ask_pet_again"])}
        state["pet_name"] = pet_name
        state["pet_display"] = pet_name
        session[APPOINTMENT_LOOKUP_STATE_KEY] = state
        session.modified = True

    rut = state.get("rut")
    pet_name = state.get("pet_name")
    if not rut or not pet_name:
        return None

    try:
        cliente = Cliente.objects.get(rut=rut)
    except Cliente.DoesNotExist:
        state["rut"] = None
        state["rut_display"] = None
        session[APPOINTMENT_LOOKUP_STATE_KEY] = state
        session.modified = True
        return {"reply": _pick_reply(APPOINTMENT_PROMPTS["client_missing"])}

    mascota = Mascota.objects.filter(cliente=cliente, nombre__iexact=pet_name).first()
    if not mascota:
        nombres = list(Mascota.objects.filter(cliente=cliente).values_list('nombre', flat=True))
        hint = ""
        if nombres:
            hint = f" Registradas tengo: {', '.join(nombres[:3])}."
        state["pet_name"] = None
        state["pet_display"] = None
        session[APPOINTMENT_LOOKUP_STATE_KEY] = state
        session.modified = True
        return {"reply": _pick_reply(APPOINTMENT_PROMPTS["pet_missing"]) + hint}

    reply = _lookup_cita_response(cliente, mascota)
    _clear_session_state(session, APPOINTMENT_LOOKUP_STATE_KEY)
    return {"reply": reply}


def _handle_availability_question(session, message: str, normalized_message: str):
    state = session.get(AVAILABILITY_STATE_KEY)
    if state is not None and not isinstance(state, dict):
        _clear_session_state(session, AVAILABILITY_STATE_KEY)
        state = None

    triggered = bool(state)
    if not triggered:
        triggered = any(keyword in normalized_message for keyword in AVAILABILITY_KEYWORDS)

    if not triggered:
        return None

    if any(word in normalized_message for word in FLOW_CANCEL_KEYWORDS):
        _clear_session_state(session, AVAILABILITY_STATE_KEY)
        return {"reply": _pick_reply(AVAILABILITY_PROMPTS["cancel"])}

    service_code = (state or {}).get("service") or _detect_service_code(normalized_message)
    target_date = _parse_requested_date(normalized_message)

    if not target_date:
        session[AVAILABILITY_STATE_KEY] = {"awaiting_date": True, "service": service_code}
        session.modified = True
        return {"reply": _pick_reply(AVAILABILITY_PROMPTS["ask_date"])}

    _clear_session_state(session, AVAILABILITY_STATE_KEY)
    reply = _build_availability_reply(target_date, service_code)
    return {"reply": reply}


def _handle_contextual_requests(session, message: str, normalized_message: str):
    appointment = _handle_appointment_lookup(session, message, normalized_message)
    if appointment:
        return appointment
    availability = _handle_availability_question(session, message, normalized_message)
    if availability:
        return availability
    return None

def _ensure_conversation(conversation_id: Optional[int]) -> Optional[ChatConversation]:
    if not conversation_id:
        return None
    try:
        return ChatConversation.objects.get(pk=conversation_id)
    except ChatConversation.DoesNotExist:
        return None

def _rate_key(request):
  ip = request.META.get("REMOTE_ADDR", "anon")
  return f"chatbot_rl:{ip}"

def _rate_limit(request):
  key = _rate_key(request)
  hits = (cache.get(key) or 0) + 1
  cache.set(key, hits, RATE_LIMIT_WINDOW)
  return hits <= RATE_LIMIT_MAX

@require_POST
def chatbot_message(request):
  # 1) Content-Type
  ctype = request.headers.get("Content-Type", "")
  if "application/json" not in ctype:
    return JsonResponse({"error": "Content-Type inválido"}, status=415)

  # 2) Rate limit
  if not _rate_limit(request):
    return JsonResponse({"error": "Demasiados mensajes. Intenta en unos segundos."}, status=429)

  # 3) Parse JSON
  try:
    payload = json.loads(request.body.decode("utf-8"))
  except Exception as e:
    logger.warning("JSON inválido: %s", e)
    return JsonResponse({"error": "JSON inválido."}, status=400)

  # 4) Validaciones de negocio
  message = (payload.get("message") or "").strip()
  if not message:
    return JsonResponse({"error": "El mensaje no puede estar vacío."}, status=400)
  if len(message) > MAX_MSG_LEN:
    return JsonResponse({"error": "Mensaje demasiado largo."}, status=400)

  # 5) Lógica de respuesta (tu función existente)
  session = request.session
  normalized_message = _normalize(message)

  conversation = _ensure_conversation(session.get(ACTIVE_CONVERSATION_KEY))
  if conversation and conversation.state != ChatConversation.STATE_CLOSED:
    client_message_obj = ChatMessage.objects.create(
        conversation=conversation,
        author=ChatMessage.AUTHOR_CLIENT,
        content=message,
    )

    staff_has_replied = conversation.messages.filter(author=ChatMessage.AUTHOR_STAFF).exists()

    if staff_has_replied:
        return JsonResponse(
            {
                "reply": None,
                "handoff": True,
                "conversation_id": conversation.pk,
                "pending_confirmation": False,
                "last_message_id": client_message_obj.id,
            }
        )

    reply_text = (
        "Nuestro equipo de recepción ya está al tanto de tu consulta. Mantén esta ventana abierta y te escribirán a la brevedad."
    )
    bot_message = ChatMessage.objects.create(
        conversation=conversation,
        author=ChatMessage.AUTHOR_BOT,
        content=reply_text,
    )
    return JsonResponse(
        {
            "reply": reply_text,
            "handoff": True,
            "conversation_id": conversation.pk,
            "pending_confirmation": False,
            "last_message_id": bot_message.id,
        }
    )

  if conversation and conversation.state == ChatConversation.STATE_CLOSED:
    session.pop(ACTIVE_CONVERSATION_KEY, None)
    session.modified = True

  pending_confirmation = session.get(HANDOFF_PENDING_KEY)
  if pending_confirmation:
    decision = _should_escalate(normalized_message)
    if decision is True:
      previous_question = session.pop(HANDOFF_MESSAGE_KEY, None)
      initial_prompt = previous_question or message
      conversation = ChatConversation.objects.create(
          source="web",
          initial_question=initial_prompt,
      )
      if previous_question:
          ChatMessage.objects.create(
              conversation=conversation,
              author=ChatMessage.AUTHOR_CLIENT,
              content=previous_question,
          )
      ChatMessage.objects.create(
          conversation=conversation,
          author=ChatMessage.AUTHOR_CLIENT,
          content=message,
      )
      reply_text = (
          "Perfecto, avisaremos a nuestra recepción para que continúe la conversación. Te contactarán en este chat."
      )
      bot_message = ChatMessage.objects.create(
          conversation=conversation,
          author=ChatMessage.AUTHOR_BOT,
          content=reply_text,
      )
      session[ACTIVE_CONVERSATION_KEY] = conversation.pk
      session[HANDOFF_PENDING_KEY] = False
      session.modified = True
      return JsonResponse(
          {
              "reply": reply_text,
              "handoff": True,
              "conversation_id": conversation.pk,
              "pending_confirmation": False,
              "last_message_id": bot_message.id,
          }
      )
    if decision is False:
      session[HANDOFF_PENDING_KEY] = False
      session.pop(HANDOFF_MESSAGE_KEY, None)
      session.modified = True
      reply_text = "¡Claro! Sigamos conversando por aquí. ¿En qué más te puedo orientar?"
      return JsonResponse(
          {
              "reply": reply_text,
              "handoff": False,
              "pending_confirmation": False,
          }
      )
    return JsonResponse(
        {
            "reply": "Solo necesito un “sí” o “no” para saber si quieres que te contacte recepción.",
            "handoff": False,
            "pending_confirmation": True,
        }
    )
  
  contextual_response = _handle_contextual_requests(session, message, normalized_message)
  if contextual_response:
    contextual_response.setdefault("handoff", False)
    contextual_response.setdefault("pending_confirmation", False)
    return JsonResponse(contextual_response)

  try:
    answer, handoff = _find_chatbot_answer(message)
    if handoff:
      session[HANDOFF_PENDING_KEY] = True
      session[HANDOFF_MESSAGE_KEY] = message
      session.modified = True
      return JsonResponse(
          {
              "reply": answer,
              "handoff": False,
              "pending_confirmation": True,
          }
      )
    session[HANDOFF_PENDING_KEY] = False
    session.pop(HANDOFF_MESSAGE_KEY, None)
    session.modified = True
    return JsonResponse({"reply": answer, "handoff": False, "pending_confirmation": False})
  except Exception as e:
    logger.exception("Error chatbot_message: %s", e)
    return JsonResponse({"error": "Error interno."}, status=500)

@require_GET
def chatbot_conversation_messages(request):
  conversation_id = request.session.get(ACTIVE_CONVERSATION_KEY)
  if not conversation_id:
    return JsonResponse({
        "messages": [],
        "state": None,
        "last_id": None,
        "conversation_id": None,
    })

  try:
    conversation = ChatConversation.objects.select_related("assigned_to").get(pk=conversation_id)
  except ChatConversation.DoesNotExist:
    request.session.pop(ACTIVE_CONVERSATION_KEY, None)
    request.session.modified = True
    return JsonResponse({
        "messages": [],
        "state": None,
        "last_id": None,
        "conversation_id": None,
    })

  after_param = request.GET.get("after")
  try:
    last_seen_id = int(after_param) if after_param else None
  except (TypeError, ValueError):
    return JsonResponse({"error": "Parámetro 'after' inválido."}, status=400)

  messages_qs = conversation.messages.select_related("staff_user")
  if last_seen_id:
    messages_qs = messages_qs.filter(id__gt=last_seen_id)

  payload = []
  last_id = last_seen_id

  for message in messages_qs:
    last_id = message.id
    payload.append(
        {
            "id": message.id,
            "author": message.author,
            "content": message.content,
            "created_at": timezone.localtime(message.created_at).isoformat(),
            "staff_user": message.staff_user.username if message.staff_user else None,
        }
    )

  return JsonResponse(
      {
          "messages": payload,
          "state": conversation.state,
          "last_id": last_id,
          "conversation_id": conversation.id,
      }
  )

def consulta_mascota(request):
    """
    Maneja la consulta de una mascota a través de un formulario.

    Args:
        request: La solicitud HTTP.

    Returns:
        HttpResponse: La respuesta HTTP que contiene el formulario de búsqueda o los resultados de la búsqueda.
    """

    # Si la solicitud es de tipo POST (es decir, el formulario fue enviado), valida un formulario (BuscarMascotaForm).
    if request.method == 'POST':
        # Pasamos los datos de la peticion al formulario
        form = BuscarMascotaForm(request.POST)

        # Si el formulario es válido, realiza una búsqueda de la mascota en la base de datos y muestra los resultados en el template.
        if form.is_valid():

            #
            rut = form.cleaned_data['rut']
            id_mascota = form.cleaned_data['id_mascota']

            # Intenta obtener los objetos. Al no existir estos causan una excepcion que manejaremos aquí.
            # Si el cliente o la mascota no existen, redirecciona a la página de consulta con un mensaje de error.
            try:
                cliente = Cliente.objects.get(rut=rut)
                mascota = Mascota.objects.prefetch_related(
                    'documentos',
                    'evoluciones__documentos',
                    'evoluciones__cita',
                ).get(
                    cliente=cliente,
                    id_mascota=id_mascota,
                )
                documentos = list(mascota.documentos.filter(evolucion__isnull=True))
                evoluciones = list(
                    mascota.evoluciones.select_related('cita', 'cita__usuario')
                    .prefetch_related('documentos')
                    .order_by('-creado_en')
                )

                today = timezone.localdate()
                edad_anios = None
                if mascota.fecha_nacimiento:
                    edad_anios = today.year - mascota.fecha_nacimiento.year - (
                        (today.month, today.day) < (
                            mascota.fecha_nacimiento.month,
                            mascota.fecha_nacimiento.day,
                        )
                    )

                contexto = {
                    'mascota': mascota,
                    'documentos': documentos,
                    'edad_mascota': edad_anios,
                    'evoluciones': evoluciones,
                    'ultima_evolucion': evoluciones[0] if evoluciones else None,
                }
                return render(request, 'ambpublica/consulta_mascota/ficha.html', contexto)
                
            except Cliente.DoesNotExist:
                rut_display = form.cleaned_data.get('rut_display', rut)
                messages.error(request, 'Cliente con Rut {} no encontrado.'.format(rut_display))
                return redirect('ambpublico_consulta')
            except Mascota.DoesNotExist:
                rut_display = form.cleaned_data.get('rut_display', rut)
                messages.error(request, 'Mascota con ID {} no encontrada para el cliente con Rut {}.'.format(id_mascota, rut_display))
                return redirect('ambpublico_consulta')

        # Si el formulario no es válido, se vuelve a renderizar el formulario con los errores.
        return render(request, 'ambpublica/consulta_mascota/form.html', {'form': form})
    else:
        # Obtener el formulario y mostrarlo.
        form = BuscarMascotaForm()
        return render(request, 'ambpublica/consulta_mascota/form.html', {'form': form})

# Maneja un flujo de pasos para la reserva de una cita.
# Utiliza la sesión para almacenar el estado del proceso de reserva.
def reserva_hora(request):
    """
    Maneja un flujo de pasos para la reserva de una cita.
    Utiliza la sesión para almacenar el estado del proceso de reserva.

    Args:
        request: La solicitud HTTP.

    Returns:
        HttpResponse: La respuesta HTTP que contiene el formulario correspondiente al paso actual o redirige a otras vistas.
    """

    # Definicion de variables por defecto
    titulo = "Seleccione el servicio que necesita."
    servicio_codigo = request.session.get('reserva_servicio')
    servicio_nombre = dict(Cita.SERVICIO_CHOICES).get(servicio_codigo)
    cliente_rut = request.session.get('reserva_c_rut_display') or request.session.get('reserva_c_rut')
    servicios_disponibles_info = None
    alternative_codes = request.session.pop('reserva_alternativas', None)

    # Verificamos si el usuario ya está en algún paso y lo asignamos a la variable
    if request.session.has_key('reserva_step'):
        step = request.session['reserva_step']
    else:
        step = ''

    if step == '':
        cleared = False
        for key in ('reserva_servicio', 'reserva_c_rut', 'reserva_c_rut_display', 'reserva_m_id'):
            if key in request.session:
                del request.session[key]
                cleared = True
        if cleared:
            servicio_codigo = None
            servicio_nombre = None
            cliente_rut = None
        request.session.pop('reserva_step', None)

    # Los pasos incluyen la creación de un cliente, una mascota, la selección de una mascota existente o la finalización del proceso.
    # Renderiza diferentes formularios y vistas según el paso actual.

    if step == "crear_cliente":
        titulo = "Por favor, ingrese sus datos."

        if 'reserva_c_rut' not in request.session or 'reserva_servicio' not in request.session:
            return redirect('ambpublico_reserva_cancelar')

        # Formulario fue enviado
        if request.method == 'POST':
            # Pasamos los datos de la peticion al formulario
            form = ClienteForm(request.POST)
            form.fields['rut'].widget = forms.HiddenInput()
            form.fields['rut'].initial = request.session['reserva_c_rut']

            # Formulario es válido, crea el cliente y lo inserta, pasa al siguiente paso
            if form.is_valid():
                request.session['reserva_c_rut'] = form.cleaned_data['rut']
                form.save()
                messages.success(request, "Se ha creado el cliente correctamente.")
                request.session['reserva_step'] = "select_mascota"
                return redirect('ambpublico_reserva')
        else:
            # Definimos el formulario para ser usado más abajo en la renderizacion del template
            form = ClienteForm()
            # Le damos el valor del RUT ingresado en el primer paso
            form.fields['rut'].initial = request.session['reserva_c_rut']
            form.fields['rut'].widget = forms.HiddenInput()
    elif step == "crear_mascota":
        titulo = "Por favor, ingrese los datos de su mascota."

        if 'reserva_c_rut' not in request.session or 'reserva_servicio' not in request.session:
            return redirect('ambpublico_reserva_cancelar')

        # Verificamos si el cliente que nos dieron anteriormente existe
        try:
            cliente = Cliente.objects.get(rut=request.session['reserva_c_rut'])

        # Nos engañaron, el cliente no existe, cancelar todo
        except Cliente.DoesNotExist:
            messages.error(request, 'Cliente no encontrado.')
            return redirect('ambpublico_reserva_cancelar')
        # Error generico
        except:
            messages.error(request, 'Ha ocurrido un error. Intente nuevamente...')
            return redirect('ambpublico_reserva_cancelar')

        # Todo bien arriba, entonces procedemos

        # Se envia el formulario
        if request.method == 'POST':

            # Pasamos los datos de la peticion al formulario
            # es_reserva nos permite para más seguridad eliminar los campos cliente e historial médico los cuales
            # solo el personal de la clinica puede manejar
            form = MascotaForm(request.POST, es_reserva=True)

            # Formulario OK, insertar la mascota, asignamos el objeto cliente que viene desde el paso anterior, vamos al siguiente paso
            if form.is_valid():
                obj = form.save(commit=False)
                obj.cliente = cliente
                obj.save()
                messages.success(request, "Se ha agregado la mascota correctamente.")
                request.session['reserva_step'] = "select_mascota"
                return redirect('ambpublico_reserva')
        else:
            # Definimos el formulario para ser usado más abajo en la renderizacion del template
            form = MascotaForm(es_reserva=True)

    elif step == "select_mascota":
        titulo = "Por favor, seleccione su mascota o agregue una nueva."

        if 'reserva_c_rut' not in request.session or 'reserva_servicio' not in request.session:
            return redirect('ambpublico_reserva_cancelar')

        # Debe el usuario crear una mascota antes de poder seleccionar?
        crear_mascota = False

        # Verificamos que existan ambos
        try:
            cliente = Cliente.objects.get(rut=request.session['reserva_c_rut'])
            mascotas = Mascota.objects.filter(cliente=cliente)

        # Nos engañaron, el cliente no existe, cancelar todo
        except Cliente.DoesNotExist:
            messages.error(request, 'Cliente no encontrado.')
            return redirect('ambpublico_reserva_cancelar')
        # Error generico
        except:
            messages.error(request, 'Ha ocurrido un error. Intente nuevamente...')
            return redirect('ambpublico_reserva_cancelar')

        # Cliente no tiene mascotas, debe crear una nueva para seguir
        if not mascotas.exists():
            crear_mascota = True

        # Obtenemos parametros (?crear_mascota=true) desde la URL en caso de que el cliente desee ingresar otra mascota
        # Ya teniendo una existente
        param_crea_mascota = request.GET.get('crear_mascota')
        if param_crea_mascota is not None and param_crea_mascota == "true":
            crear_mascota = True

        # Debemos ir a crear mascota entonces?
        if crear_mascota == True:
            request.session['reserva_step'] = "crear_mascota"
            return redirect('ambpublico_reserva')

        # Ok, no vamos a ir a crear mascota, seguimos con la seleccion

        # Cargamos proceso de seleccion para el final
        # Definimos el formulario para ser usado más abajo en la renderizacion del template
        # Usamos queryset para obtener los objetos en el modelo y mostrarlos en el select del formulario
        form = MascotaSelectForm(queryset=mascotas)

        # Se envia el formulario
        if request.method == 'POST':
            # Pasamos los datos de la peticion al formulario
            # Usamos queryset para obtener los objetos en el modelo y mostrarlos en el select del formulario
            # Es necesario hacerlo nuevamente para la validacion del formulario
            form = MascotaSelectForm(request.POST, queryset=mascotas)
            # Formulario es válido, guardamos el ID de la mascota, vamos al paso final
            if form.is_valid():
                request.session['reserva_m_id'] = form.cleaned_data['mascota']
                request.session['reserva_step'] = "final"
                return redirect('ambpublico_reserva')
    elif step == "final":

        if 'reserva_c_rut' not in request.session or 'reserva_m_id' not in request.session or 'reserva_servicio' not in request.session:
            return redirect('ambpublico_reserva_cancelar')
        
        # Intentamos obtener el cliente y la mascota
        try:
            cliente = Cliente.objects.get(rut=request.session['reserva_c_rut'])
            # La mascota debe pertenecer al Cliente, si no, nos ingresaron cualquier cosa
            mascota = Mascota.objects.get(cliente=cliente, id_mascota=request.session['reserva_m_id'])
        # Nos engañaron, el cliente o la mascota no existe, cancelar todo
        except (Cliente.DoesNotExist, Mascota.DoesNotExist):
            messages.error(request, 'No se ha encontrado la información ingresada. Intente nuevamente...')
            return redirect('ambpublico_reserva_cancelar')
        # Error generico
        except:
            messages.error(request, 'Ha ocurrido un error. Intente nuevamente...')
            return redirect('ambpublico_reserva_cancelar')

        # Se envia el formulario
        if request.method == 'POST':
            # Pasamos los datos de la peticion al formulario
            form = CitaForm(request.POST, servicio=servicio_codigo)

            # Todo OK
            if form.is_valid():
                # Obtener el valor de la nueva cita
                n_cita = form.cleaned_data['n_cita']

                # Verificamos que la cita ingresada sea real, ingresamos los datos del cliente y la mascota a ella
                try:
                    cita = Cita.objects.get(n_cita=n_cita, servicio=servicio_codigo)
                    if cita.estado != '0':
                        messages.error(request, 'Lo sentimos, la cita seleccionada ya no está disponible.')
                        return redirect('ambpublico_reserva_cancelar')
                    cita.estado = '1'
                    cita.cliente = cliente
                    cita.mascota = mascota
                    cita.save()

                    # Intenta enviar un correo de confirmación al cliente
                    try:
                        cita_fecha = cita.fecha
                        if timezone.is_naive(cita_fecha):
                            cita_fecha = timezone.make_aware(cita_fecha, timezone.get_current_timezone())
                        cita_fecha = timezone.localtime(cita_fecha)

                        veterinario_nombre = cita.usuario.get_full_name().strip() or cita.usuario.get_username()
                        cita_fecha_str = date_format(cita_fecha, "DATETIME_FORMAT")

                        servicio_str = dict(Cita.SERVICIO_CHOICES).get(cita.servicio, cita.servicio)

                        text_body = (
                            f"Hola {cliente.nombre_cliente},\n\n"
                            f"Tu reserva fue agendada para el {cita_fecha_str} con el/la veterinario(a) {veterinario_nombre}.\n"
                            f"RUT: {cliente.rut}.\n\n"
                            f"Mascota: {mascota.nombre}.\n"
                            f"N° de Cita: {cita.n_cita}.\n"
                            f"Servicio: {servicio_str}.\n\n"
                            "Te esperamos en Veterinaria de Arce.\n\n"
                            "Si no puedes asistir, avísanos con anticipación.\n\n"
                            "Saludos,\n"
                            "Veterinaria de Arce"
                        )

                        logo_url = "https://i.postimg.cc/x1RJ1G0t/Logovetarce.png"
                        html_body = f"""
                        <div style="font-family:Arial,Helvetica,sans-serif; color:#333; line-height:1.6; max-width:600px; margin:auto; border:1px solid #e0e0e0; border-radius:10px; padding:20px;">
                            <div style="text-align:center; margin-bottom:20px;">
                                <img src="{logo_url}" alt="Logo Veterinaria de Arce" style="width:120px; height:auto;">
                            </div>
                            <h2 style="color:#1a73e8; text-align:center;">¡Tu cita está confirmada!</h2>
                            <p>Hola <strong>{cliente.nombre_cliente}</strong>,</p>
                            <p>Hemos agendado tu cita en <strong>Veterinaria de Arce</strong>.</p>
                            <div style="background:#f7fbff; border:1px solid #d1e7ff; border-radius:8px; padding:16px; margin:18px 0;">
                                <p style="margin:0 0 8px 0;"><strong>RUT:</strong> {cliente.rut}</p>
                                <p style="margin:0 0 8px 0;"><strong>Fecha y hora:</strong> {cita_fecha_str}</p>
                                <p style="margin:0 0 8px 0;"><strong>Veterinario(a):</strong> {veterinario_nombre}</p>
                                <p style="margin:0 0 8px 0;"><strong>Mascota:</strong> {mascota.nombre}</p>
                                <p style="margin:0 0 8px 0;"><strong>N° de Cita:</strong> {cita.n_cita}</p>
                                <p style="margin:0;"><strong>Servicio:</strong> {servicio_str}</p>
                            </div>
                            <p>Te esperamos en nuestra clínica. Si no puedes asistir, avísanos con anticipación para reagendar tu hora o cancélala en la sección reserva de horas.</p>
                            <hr style="margin:20px 0; border:none; border-top:1px solid #ddd;">
                            <p style="text-align:center; font-size:14px; color:#555;">
                                — Equipo de <strong>Veterinaria de Arce 🐾</strong><br>
                                <a href="https://tusitio.cl" style="color:#1a73e8; text-decoration:none;">www.veterinariadearce.cl</a>
                            </p>
                        </div>
                        """

                        message = EmailMultiAlternatives(
                            subject="Confirmación de reserva - Veterinaria de Arce",
                            body=text_body,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            to=[cliente.email],
                            headers={"Reply-To": "shadowxd41@gmail.com"},
                        )
                        message.attach_alternative(html_body, "text/html")
                        message.send(fail_silently=False)
                    except Exception as email_error:
                        logger.warning("No se pudo enviar el correo de confirmación para la cita %s: %s", cita.n_cita, email_error)
                        
                # Error generico
                except:
                    messages.error(request, 'Ha ocurrido un error. Intente nuevamente...')
                    return redirect('ambpublico_reserva_cancelar')

                # Construir payload y limpiar sesión
                confirmation_payload = _build_confirmation_payload(
                    cita,
                    cliente=cliente,
                    mascota=mascota,
                )
                request.session['reserva_confirmacion'] = confirmation_payload

                request.session.pop('reserva_step', None)
                for key in ('reserva_servicio', 'reserva_c_rut', 'reserva_c_rut_display', 'reserva_m_id'):
                    request.session.pop(key, None)

                # Redirigir a comprobante con parámetro GET
                confirm_url = f"{reverse('ambpublico_reserva_confirmacion')}?cita={cita.n_cita}"
                return redirect(confirm_url)

        # Definimos el formulario para ser usado más abajo en la renderizacion del template
        form = CitaForm(servicio=servicio_codigo)

        # Contexto distinto para mostrar toda la información en el resumen ya que es el paso final
        context = {
            'form': form,
            'step': step,
            'mascota': mascota,
            'cliente': cliente,
            'servicio_nombre': servicio_nombre,
            'available_slots': getattr(form, 'available_slots', []),
        }

        # Hacemos return aquí para que no se cargue el contexto de más abajo
        return render(request, 'ambpublica/reserva_horas/form.html', context)
    elif step == "ingresar_rut":
        titulo = "Por favor, ingrese su RUT."

        if 'reserva_servicio' not in request.session:
            return redirect('ambpublico_reserva_cancelar')

        if not Cita.objects.filter(estado='0', servicio=servicio_codigo).exists():
            available_services = list(
                Cita.objects.filter(estado='0').values_list('servicio', flat=True).distinct()
            )
            request.session['reserva_step'] = ''
            request.session.pop('reserva_servicio', None)
            request.session.pop('reserva_c_rut', None)
            request.session.pop('reserva_c_rut_display', None)
            request.session['reserva_alternativas'] = [
                code for code in available_services if code != servicio_codigo
            ]
            messages.error(
                request,
                'Lo sentimos, el servicio seleccionado se quedó sin horas disponibles. Revisa otras opciones.',
            )
            return redirect('ambpublico_reserva')

        if request.method == 'POST':
            form = RutForm(request.POST)
            if form.is_valid():
                rut = form.cleaned_data['rut']
                rut_display = form.cleaned_data.get('rut_display', str(rut))
                cliente = Cliente.objects.filter(rut=rut).first()

                request.session['reserva_c_rut'] = rut
                request.session['reserva_c_rut_display'] = rut_display

                if cliente:
                    request.session['reserva_step'] = "select_mascota"
                else:
                    request.session['reserva_step'] = "crear_cliente"
                return redirect('ambpublico_reserva')
        else:
            form = RutForm()
    else:
        citas = Cita.objects.filter(estado='0')

        if not citas.exists():
            context = {
                'step': 'nohours',
                'progress': _get_progress_state('nohours'),
                'service_highlights': _build_service_highlights(),
            }
            return render(request, 'ambpublica/reserva_horas/form.html', context)
        
        servicios_disponibles = list(citas.values_list('servicio', flat=True).distinct())

        if not servicios_disponibles:
            context = {
                'step': 'nohours',
                'progress': _get_progress_state('nohours'),
                'service_highlights': _build_service_highlights(),
            }
            return render(request, 'ambpublica/reserva_horas/form.html', context)

        servicios_disponibles_info = _build_service_highlights(servicios_disponibles)

        if request.method == 'POST':
            form = ServicioForm(request.POST, available_services=servicios_disponibles)
            if form.is_valid():
                servicio = form.cleaned_data['servicio']

                if not Cita.objects.filter(estado='0', servicio=servicio).exists():
                    messages.error(request, 'No hay citas disponibles para el servicio seleccionado.')
                else:
                    request.session['reserva_servicio'] = servicio
                    request.session['reserva_step'] = "ingresar_rut"
                    return redirect('ambpublico_reserva')
        else:
            form = ServicioForm(available_services=servicios_disponibles)

    # Definimos las diferentes variables mediante el contexto Django
    context = {
        'titulo': titulo,
        'form': form,
        'step': step,
        'service_highlights': _build_service_highlights(),
        'progress': _get_progress_state(step),
    }
    if servicio_nombre:
        context['servicio_nombre'] = servicio_nombre
    if cliente_rut:
        context['cliente_rut'] = cliente_rut
    if servicios_disponibles_info:
        context['servicios_disponibles'] = servicios_disponibles_info
    if alternative_codes:
        context['servicios_alternativos'] = _build_service_highlights(alternative_codes)
    return render(request, 'ambpublica/reserva_horas/form.html', context)

def reserva_hora_confirmacion(request):
    """Muestra el resumen de una cita recién confirmada."""

    confirmation = request.session.get('reserva_confirmacion')

    if not confirmation:
        cita_id = request.GET.get('cita')
        if cita_id:
            try:
                cita = Cita.objects.select_related('cliente', 'mascota', 'usuario').get(n_cita=cita_id)
            except (Cita.DoesNotExist, ValueError):
                cita = None
            else:
                if cita.estado == '1' and cita.cliente and cita.mascota:
                    confirmation = _build_confirmation_payload(cita)

    if not confirmation:
        messages.error(
            request,
            'No pudimos mostrar el comprobante de tu reserva recién confirmada. Por favor, revisa tu correo o inicia una nueva solicitud.',
        )
        return redirect('ambpublico_reserva')

    context = {
        'step': 'success',
        'progress': _get_progress_state('success'),
        'confirmation': confirmation,
    }

    request.session.pop('reserva_confirmacion', None)

    return render(request, 'ambpublica/reserva_horas/confirmacion_exitosa.html', context)

# Funcion simple para eliminar la variable de sesion para cancelar el proceso de reserva
def reserva_hora_cancelar(request):
    """
    Cancela el proceso de reserva eliminando la variable de sesión.

    Args:
        request: La solicitud HTTP.

    Returns:
        HttpResponse: La respuesta HTTP que redirige a la vista de reserva.
    """
    for key in ('reserva_step', 'reserva_servicio', 'reserva_c_rut', 'reserva_c_rut_display', 'reserva_m_id'):
        try:
            del request.session[key]
        except:
            pass
    messages.success(request, "El proceso de reserva ha sido cancelado.")
    return redirect('ambpublico_reserva')


def cancelar_cita(request):
    """Permite que un cliente cancele su cita reservada."""

    success_message = None
    if request.method == 'POST':
        form = CancelarCitaForm(request.POST)
        if form.is_valid():
            rut = form.cleaned_data['rut']
            rut_display = form.cleaned_data.get('rut_display', '')
            n_cita = form.cleaned_data['n_cita']

            rut_variants = {rut}
            if rut_display:
                parts = rut_display.rsplit('-', 1)
                if len(parts) == 2:
                    dv = parts[1].strip()
                    if dv.isdigit():
                        try:
                            rut_variants.add(int(f"{rut}{dv}"))
                        except ValueError:
                            pass

            cita = (
                Cita.objects.select_related('cliente')
                .filter(
                    n_cita=n_cita,
                    cliente__isnull=False,
                    cliente__rut__in=list(rut_variants),
                )
                .first()
            )

            if not cita:
                form.add_error(None, 'No se encontró una cita registrada con los datos ingresados.')
            elif cita.estado == '2':
                form.add_error(None, 'La cita ingresada ya fue cancelada anteriormente.')
            elif cita.estado == '0':
                form.add_error(None, 'La cita ingresada aún no se encuentra reservada.')
            else:
                cita.estado = '2'
                cita.asistencia = None
                cita.save(update_fields=['estado', 'asistencia'])
                success_message = 'Tu cita ha sido cancelada exitosamente.'

                cliente = cita.cliente
                mascota = cita.mascota
                fecha_local = timezone.localtime(cita.fecha)
                fecha_formateada = fecha_local.strftime('%d-%m-%Y')
                hora_formateada = fecha_local.strftime('%H:%M')
                servicio_nombre = cita.get_servicio_display()
                rut_formateado = rut_display or str(cliente.rut)

                mensaje_correo = (
                    "Se ha cancelado una cita desde el portal público.\n\n"
                    f"Número de cita: {cita.n_cita}\n"
                    f"Cliente: {cliente.nombre_cliente}\n"
                    f"RUT: {rut_formateado}\n"
                    f"Mascota: {mascota.nombre if mascota else 'Sin información'}\n"
                    f"Servicio: {servicio_nombre}\n"
                    f"Fecha: {fecha_formateada}\n"
                    f"Hora: {hora_formateada}"
                )

                try:
                    send_mail(
                        f"Cita cancelada #{cita.n_cita}",
                        mensaje_correo,
                        settings.DEFAULT_FROM_EMAIL,
                        [getattr(settings, 'CONTACT_EMAIL', settings.DEFAULT_FROM_EMAIL)],
                        fail_silently=False,
                    )
                except Exception as email_error:
                    logger.warning(
                        "No se pudo enviar el correo de cancelación para la cita %s: %s",
                        cita.n_cita,
                        email_error,
                    )

                form = CancelarCitaForm()
    else:
        form = CancelarCitaForm()

    context = {
        'form': form,
        'success_message': success_message,
    }
    return render(request, 'ambpublica/reserva_horas/cancelar_cita.html', context)