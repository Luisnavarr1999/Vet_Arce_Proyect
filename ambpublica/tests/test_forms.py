from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ambpublica.forms import CancelarCitaForm, CitaForm, RutForm, ServicioForm
from paneltrabajador.models import Cita


class BaseFormTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="veterinario", email="vet@example.com", password="secret"
        )


class CitaFormTests(BaseFormTest):
    def test_only_available_appointments_are_listed(self):
        future = timezone.now() + timedelta(days=1)
        taken = Cita.objects.create(
            estado="1",
            usuario=self.user,
            fecha=future,
            servicio="general",
        )
        available = Cita.objects.create(
            estado="0",
            usuario=self.user,
            fecha=future,
            servicio="general",
        )
        form = CitaForm()
        choices = dict(form.fields["n_cita"].choices)
        self.assertIn(available.n_cita, choices)
        self.assertNotIn(taken.n_cita, choices)

    def test_filters_by_service(self):
        future = timezone.now() + timedelta(days=1)
        general = Cita.objects.create(
            estado="0",
            usuario=self.user,
            fecha=future,
            servicio="general",
        )
        dental = Cita.objects.create(
            estado="0",
            usuario=self.user,
            fecha=future,
            servicio="dentista",
        )
        form = CitaForm(servicio="dentista")
        choices = dict(form.fields["n_cita"].choices)
        self.assertIn(dental.n_cita, choices)
        self.assertNotIn(general.n_cita, choices)


class RutDisplayMixinTests(BaseFormTest):
    def test_rut_clean_returns_number_and_stores_display(self):
        form = RutForm(data={"rut": "12.345.678-5"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["rut"], 12345678)
        self.assertEqual(form.cleaned_data["rut_display"], "12.345.678-5")

    def test_cancelar_cita_form_normalizes_rut(self):
        form = CancelarCitaForm(data={"rut": "12345678", "n_cita": 10})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["rut"], 12345678)
        self.assertEqual(form.cleaned_data["rut_display"], "12.345.678-5")


class ServicioFormTests(BaseFormTest):
    def test_limits_choices_when_available_services_provided(self):
        form = ServicioForm(available_services={"cirugia"})
        choices = list(form.fields["servicio"].choices)
        self.assertEqual(choices, [("cirugia", "Cirugía")])