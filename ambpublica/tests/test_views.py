from unittest import mock

from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.http import HttpResponse

from ambpublica.views import _rule_based_answer


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
    def test_greeting_intent(self):
        reply, needs_handoff = _rule_based_answer("Hola, ¿hay horas disponibles?")
        self.assertIn("Hola", reply)
        self.assertFalse(needs_handoff)

    def test_fallback_response(self):
        reply, needs_handoff = _rule_based_answer("Pregunta irreconocible")
        self.assertTrue(needs_handoff)
        self.assertIn("No estoy seguro", reply)