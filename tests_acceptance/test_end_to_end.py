from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from paneltrabajador.models import Cita, Cliente, Mascota


class AppointmentEndToEndTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.base_url = cls.live_server_url

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):
        self.driver = Client()
        self.panel_driver = Client()
        self.password = "Seguro12345"

        veterinarios, _ = Group.objects.get_or_create(name="veterinario")
        user_perms = Permission.objects.filter(
            codename__in=[
                "view_cita",
                "add_cita",
                "change_cita",
                "delete_cita",
            ]
        )

        self.veterinario = get_user_model().objects.create_user(
            username="vet",
            email="vet@example.com",
            password=self.password,
        )
        self.veterinario.groups.add(veterinarios)
        self.veterinario.user_permissions.set(user_perms)

        self.cliente = Cliente.objects.create(
            rut=12345678,
            nombre_cliente="Cliente Demo",
            direccion="Calle Falsa 123",
            telefono="123456789",
            email="cliente@example.com",
        )
        self.mascota = Mascota.objects.create(
            nombre="Firulais",
            numero_chip=999,
            especie="Perro",
            raza="Mestizo",
            fecha_nacimiento=timezone.now().date(),
            cliente=self.cliente,
        )
        self.disponible = Cita.objects.create(
            estado="0",
            usuario=self.veterinario,
            fecha=timezone.now() + timedelta(days=1),
            servicio="general",
        )

    def _format_datetime(self, dt):
        aware_dt = dt
        if timezone.is_naive(aware_dt):
            aware_dt = timezone.make_aware(dt, timezone.get_current_timezone())
        return timezone.localtime(aware_dt).strftime("%Y-%m-%dT%H:%M")

    def _complete_public_reservation(self):
        reserva_url = reverse("ambpublico_reserva")

        future_slot = timezone.now() + timedelta(days=2)
        self.disponible.refresh_from_db()
        self.disponible.estado = "0"
        self.disponible.fecha = future_slot
        self.disponible.cliente = None
        self.disponible.mascota = None
        self.disponible.save()

        response = self.driver.get(reserva_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["step"], "")

        response = self.driver.post(reserva_url, {"servicio": self.disponible.servicio})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.driver.session["reserva_step"], "ingresar_rut")

        response = self.driver.get(reserva_url)
        self.assertEqual(response.context["step"], "ingresar_rut")

        response = self.driver.post(reserva_url, {"rut": str(self.cliente.rut)})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.driver.session["reserva_step"], "select_mascota")

        response = self.driver.get(reserva_url)
        self.assertEqual(response.context["step"], "select_mascota")

        response = self.driver.post(reserva_url, {"mascota": str(self.mascota.id_mascota)})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.driver.session["reserva_step"], "final")

        response = self.driver.get(reserva_url)
        self.assertEqual(response.context["step"], "final")

        available_slots = response.context.get("available_slots", [])
        slot_id = str(self.disponible.n_cita)
        self.assertTrue(any(slot.get("id") == slot_id for slot in available_slots))

        response = self.driver.post(reserva_url, {"n_cita": slot_id})
        self.assertEqual(response.status_code, 302)

        confirmation_response = self.driver.get(response["Location"])
        self.assertEqual(confirmation_response.status_code, 200)

        cita = Cita.objects.get(pk=self.disponible.pk)
        self.assertEqual(cita.estado, "1")
        self.assertEqual(cita.cliente, self.cliente)
        self.assertEqual(cita.mascota, self.mascota)

        confirmation = confirmation_response.context["confirmation"]
        self.assertEqual(confirmation["numero_cita"], cita.n_cita)
        self.assertEqual(confirmation["cliente"]["nombre"], self.cliente.nombre_cliente)
        self.assertEqual(confirmation["mascota"]["nombre"], self.mascota.nombre)

        return cita

    def test_public_user_can_reserve_an_appointment(self):
        cita = self._complete_public_reservation()
        self.assertEqual(cita.estado, "1")

    def test_panel_can_cancel_reserved_appointment(self):
        cita = self._complete_public_reservation()

        login_response = self.panel_driver.post(
            reverse("panel_home"),
            {"username": self.veterinario.username, "password": self.password},
        )
        self.assertEqual(login_response.status_code, 302)

        edit_url = reverse("panel_cita_editar", args=[cita.n_cita])
        response = self.panel_driver.get(edit_url)
        self.assertEqual(response.status_code, 200)

        payload = {
            "cliente": cita.cliente.pk,
            "mascota": cita.mascota.pk,
            "servicio": cita.servicio,
            "estado": "2",
            "usuario": cita.usuario.pk,
            "fecha": self._format_datetime(cita.fecha),
            "asistencia": "",
        }
        response = self.panel_driver.post(edit_url, payload)
        self.assertEqual(response.status_code, 302)

        cita.refresh_from_db()
        self.assertEqual(cita.estado, "2")
        self.assertIsNone(cita.asistencia)
