import json
import unicodedata
from datetime import timedelta
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.http import HttpResponse
from django.utils import timezone

from ambpublica.views import _rule_based_answer
from paneltrabajador.models import Cita, Cliente, Mascota


def _normalize(text):
    return "".join(
        c for c in unicodedata.normalize("NFD", text.lower()) if unicodedata.category(c) != "Mn"
    )


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="noreply@example.com",
)
class MainViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    @mock.patch("ambpublica.views.send_mail", return_value=1)
    def test_successful_contact_submission_sends_mail(self, mock_send_mail):
        with mock.patch("ambpublica.views.render", return_value=HttpResponse("ok")) as mocked_render:
            response = self.client.post(
                reverse("ambpublico_index"),
                data={"nombre": "Juan", "correo": "juan@example.com", "mensaje": "Hola"},
            )
        self.assertEqual(response.status_code, 200)
        args, kwargs = mocked_render.call_args
        context = kwargs.get("context", args[2])
        self.assertTrue(context["contact_success"])
        self.assertIsNone(context["contact_error"])
        mock_send_mail.assert_called_once()

    @mock.patch("ambpublica.views.send_mail", side_effect=Exception("boom"))
    def test_contact_failure_sets_error_message(self, mock_send_mail):
        with mock.patch("ambpublica.views.render", return_value=HttpResponse("ok")) as mocked_render:
            response = self.client.post(
                reverse("ambpublico_index"),
                data={"nombre": "Juan", "correo": "juan@example.com", "mensaje": "Hola"},
            )
        self.assertEqual(response.status_code, 200)
        args, kwargs = mocked_render.call_args
        context = kwargs.get("context", args[2])
        self.assertFalse(context["contact_success"])
        self.assertIsNotNone(context["contact_error"])
        mock_send_mail.assert_called_once()


class RuleBasedChatbotTests(TestCase):
    @mock.patch("ambpublica.views.random.choice", side_effect=lambda seq: seq[0])
    def test_greeting_intent(self, mock_choice):
        reply, needs_handoff = _rule_based_answer("Hola, ¿hay horas disponibles?")
        self.assertIn("Hola", reply)
        self.assertFalse(needs_handoff)

    @mock.patch("ambpublica.views.random.choice", side_effect=lambda seq: seq[0])
    def test_fallback_response(self, mock_choice):
        reply, needs_handoff = _rule_based_answer("Pregunta irreconocible")
        self.assertTrue(needs_handoff)
        self.assertIn("recepcionista humana", reply)


class ChatbotFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("ambpublico_chatbot_message")
        self.staff = get_user_model().objects.create_user(username="vet", password="pass1234")
        self.cliente = Cliente.objects.create(
            rut=12345678,
            nombre_cliente="Juan Pérez",
            direccion="Av. Siempre Viva 123",
            telefono="+56912345678",
            email="juan@example.com",
        )
        self.mascota = Mascota.objects.create(
            nombre="Firulais",
            numero_chip=1234567890123,
            especie="Perro",
            raza="Mestizo",
            fecha_nacimiento=timezone.now().date(),
            cliente=self.cliente,
            historial_medico="",
        )
        Cita.objects.create(
            cliente=self.cliente,
            mascota=self.mascota,
            estado='1',
            usuario=self.staff,
            fecha=timezone.now() + timedelta(days=1),
            servicio='general',
        )

    def _post(self, message: str):
        return self.client.post(
            self.url,
            data=json.dumps({"message": message}),
            content_type="application/json",
        )

    @mock.patch("ambpublica.views.random.choice", side_effect=lambda seq: seq[0])
    def test_appointment_lookup_flow_returns_upcoming_booking(self, mock_choice):
        response = self._post("¿Tengo alguna cita agendada?")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("RUT", data["reply"])
        self.assertFalse(data["handoff"])

        response = self._post(str(self.cliente.rut))
        data = response.json()
        self.assertIn("mascota", _normalize(data["reply"]))

        response = self._post(self.mascota.nombre)
        data = response.json()
        self.assertIn("tienes una", _normalize(data["reply"]))
        self.assertFalse(data["handoff"])

    @mock.patch("ambpublica.views.random.choice", side_effect=lambda seq: seq[0])
    def test_availability_query_by_weekday(self, mock_choice):
        target_dt = timezone.now() + timedelta(days=2)
        target_dt = target_dt.replace(hour=10, minute=0, second=0, microsecond=0)
        Cita.objects.create(
            cliente=None,
            mascota=None,
            estado='0',
            usuario=self.staff,
            fecha=target_dt,
            servicio='general',
        )

        weekday_names = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
        day_keyword = weekday_names[target_dt.weekday()]

        response = self._post(f"¿Hay horas disponibles el {day_keyword}?")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        normalized_reply = _normalize(data["reply"])
        self.assertIn(day_keyword, normalized_reply)
        self.assertTrue("cupo" in normalized_reply or "horario" in normalized_reply)
        self.assertFalse(data["handoff"])