from ast import And
from urllib import request
from django.shortcuts import redirect, render
from django.template import loader
from django import forms
from django.contrib import messages
from ambpublica.forms import ContactForm, BuscarMascotaForm, CancelarCitaForm, CitaForm, MascotaSelectForm, RutForm, ServicioForm
from paneltrabajador.forms import ClienteForm, MascotaForm
from paneltrabajador.models import Cita, Cliente, Mascota

import json
from django.http import HttpResponse, JsonResponse
import logging
from django.core.cache import cache
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.formats import date_format
from django.core.mail import EmailMultiAlternatives

from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
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
    }

    return render(request, 'ambpublica/main.html', context)

# cosas que responde el chat demo

def _normalize(txt: str) -> str:
    # minúsculas + sin acentos
    txt = txt.lower()
    txt = unicodedata.normalize("NFD", txt)
    return "".join(c for c in txt if unicodedata.category(c) != "Mn")

# Cada intent tiene un patrón regex y una respuesta
INTENTS = [
    # Saludo / Despedida
    (re.compile(r"^(ola|hola|buenas|buenos dias|buenas tardes|buenas noches)\b"), 
     "¡Hola! 😊 Soy el asistente de la Veterinaria de Arce. ¿En qué te ayudo?"),
    (re.compile(r"\b(gracias|chau|adios|adiós|nos vemos)\b"), 
     "¡Gracias por escribirnos! 🐾"),

    # Horarios
    (re.compile(r"\b(horario|horarios|abren|cierran|apertura|cierre)\b"), 
     "Atendemos de lunes a viernes 09:00–19:00 y sábados 10:00–14:00 🕘"),

    # Ubicación
    (re.compile(r"\b(ubicacion|ubicación|direccion|dirección|donde|dónde|como llegar)\b"), 
     "Estamos en Santiago Centro. En la sección Contacto tienes el mapa exacto 📍"),

    # Contacto
    (re.compile(r"\b(contacto|telefono|teléfono|whatsapp|correo|email)\b"), 
     "Puedes escribirnos por este chat o llamarnos a recepción. También respondemos por correo."),

    # Servicios y precios
    (re.compile(r"\b(servicio|servicios|vacuna|vacunas|cirugia|cirugía|dentista|odontologia|peluquer|baño|desparasita)\b"), 
     "Ofrecemos consulta general, vacunas, odontología y cirugías. ¿Qué servicio te interesa?"),
    (re.compile(r"\b(precio|precios|cuanto cuesta|tarifa|valen)\b"), 
     "Los precios varían según el servicio y la mascota. Podemos orientarte por aquí y confirmas en recepción 💳"),

    # Pagos
    (re.compile(r"\b(pago|pagos|tarjeta|efectivo|transfer|transferencia|webpay|promocion|promoción)\b"), 
     "Aceptamos tarjeta, transferencia y efectivo. Pregunta en recepción por promociones 💳"),

    # Reservas / Cancelaciones
    (re.compile(r"\b(reserv(ar|a)|agendar|sacar hora|cita nueva)\b"), 
     "Puedes reservar desde “Reserva de Horas Online”. Si quieres, te voy guiando paso a paso 👍"),
    (re.compile(r"\b(cancelar (cita|hora)|anular (cita|hora)|reagendar|cambiar hora)\b"), 
     "Para cancelar o reagendar, indícanos tu número de cita o contáctanos por recepción."),

    # Emergencias
    (re.compile(r"\b(emergencia|emergencias|urgencia|urgencias|fuera de horario)\b"), 
     "Para emergencias fuera de horario, llámanos y coordinamos ayuda 📞"),

    # Políticas / tiempos / requisitos
    (re.compile(r"\b(politica|política|no show|atraso|tarde|cancelacion|cancelación)\b"), 
     "Si no puedes asistir, avísanos con anticipación para liberar el cupo. ¡Gracias! 🙏"),
    (re.compile(r"\b(tiempo|demora|cola|espera|cuanto se demoran)\b"), 
     "El tiempo de atención depende del día y la demanda. ¡Hacemos lo posible por atender rápido!"),
    (re.compile(r"\b(requisito|requisitos|primera consulta|documento|documentos)\b"), 
     "Trae el RUT del tutor y, si tienes, el historial o carnet de tu mascota."),
    
    # Otros comunes
    (re.compile(r"\b(estacionamiento|parking)\b"), 
     "Tenemos estacionamiento cercano con convenios en ciertos horarios."),
    (re.compile(r"\b(exotica|exótica|aves|reptil|reptiles|huron|hurón)\b"), 
     "Atendemos mascotas comunes. Para exóticos, consúltanos caso a caso."),
    (re.compile(r"\b(domicilio|a domicilio|visita a domicilio)\b"), 
     "Podemos coordinar visitas a domicilio en zonas cercanas. Escríbenos para evaluar."),
]

def _rule_based_answer(message: str) -> tuple[str, bool]:
    q = _normalize(message)
    for pattern, reply in INTENTS:
        if pattern.search(q):
            return reply, False
    # fallback
    return ("No estoy seguro de cómo ayudarte con eso. ¿Quieres que avise a recepción para que te contacten?", True)

def _find_chatbot_answer(message: str):
    return _rule_based_answer(message)

logger = logging.getLogger(__name__)

MAX_MSG_LEN = 500          # Máximo ancho de mensaje aceptado
RATE_LIMIT_WINDOW = 30     # Ventana en segundos
RATE_LIMIT_MAX = 15        # Máximo de mensajes por ventana e IP

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
  try:
    answer, handoff = _find_chatbot_answer(message)
    return JsonResponse({"reply": answer, "handoff": handoff})
  except Exception as e:
    logger.exception("Error chatbot_message: %s", e)
    return JsonResponse({"error": "Error interno."}, status=500)


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
                mascota = Mascota.objects.prefetch_related('documentos').get(
                cliente=cliente, id_mascota=id_mascota)
                contexto = {
                    'mascota': mascota,
                    'documentos': mascota.documentos.all(),
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
                            f"Mascota: {mascota.nombre}.\n\n"
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
                                <p style="margin:0 0 8px 0;"><strong>Fecha y hora:</strong> {cita_fecha_str}</p>
                                <p style="margin:0 0 8px 0;"><strong>Veterinario(a):</strong> {veterinario_nombre}</p>
                                <p style="margin:0 0 8px 0;"><strong>Mascota:</strong> {mascota.nombre}</p>
                                <p style="margin:0 0 8px 0;"><strong>N° de Cita:</strong> {cita.n_cita}</p>
                                <p style="margin:0;"><strong>Servicio:</strong> {servicio_str}</p>
                            </div>
                            <p>Te esperamos en nuestra clínica. Si no puedes asistir, avísanos con anticipación para reagendar tu hora.</p>
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

                # Eliminamos el paso para que se devuelva al inicio
                try:
                    del request.session['reserva_step']
                except:
                    pass
                for key in ('reserva_servicio', 'reserva_c_rut', 'reserva_c_rut_display', 'reserva_m_id'):
                    try:
                        del request.session[key]
                    except:
                        pass

                # Todo OK, nos devolvemos
                messages.success(request, '¡Se ha reservado su hora exitosamente!')
                return redirect('ambpublico_reserva')

        # Definimos el formulario para ser usado más abajo en la renderizacion del template
        form = CitaForm(servicio=servicio_codigo)

        # Contexto distinto para mostrar toda la información en el resumen ya que es el paso final
        context = {
            'form': form,
            'step': step,
            'mascota': mascota,
            'cliente': cliente,
            'servicio_nombre': servicio_nombre,
        }

        # Hacemos return aquí para que no se cargue el contexto de más abajo
        return render(request, 'ambpublica/reserva_horas/form.html', context)
    elif step == "ingresar_rut":
        titulo = "Por favor, ingrese su RUT."

        if 'reserva_servicio' not in request.session:
            return redirect('ambpublico_reserva_cancelar')

        if not Cita.objects.filter(estado='0', servicio=servicio_codigo).exists():
            messages.error(request, 'Lo sentimos, ya no quedan citas disponibles para el servicio seleccionado.')
            return redirect('ambpublico_reserva_cancelar')

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
            return render(request, 'ambpublica/reserva_horas/form.html', {'step': 'nohours'})
        
        servicios_disponibles = list(citas.values_list('servicio', flat=True).distinct())

        if not servicios_disponibles:
            return render(request, 'ambpublica/reserva_horas/form.html', {'step': 'nohours'})

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
    context = {'titulo': titulo, 'form': form, 'step': step}
    if servicio_nombre:
        context['servicio_nombre'] = servicio_nombre
    if cliente_rut:
        context['cliente_rut'] = cliente_rut
    return render(request, 'ambpublica/reserva_horas/form.html', context)

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
                cita.save(update_fields=['estado'])
                success_message = 'Tu cita ha sido cancelada exitosamente.'
                form = CancelarCitaForm()
    else:
        form = CancelarCitaForm()

    context = {
        'form': form,
        'success_message': success_message,
    }
    return render(request, 'ambpublica/reserva_horas/cancelar_cita.html', context)