from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from paneltrabajador.models import Cita, Cliente, Mascota


class CitaViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.group, _ = Group.objects.get_or_create(name="veterinario")
        permissions = Permission.objects.filter(
            codename__in=["add_cita", "change_cita"]
        )
        cls.veterinario = get_user_model().objects.create_user(
            username="veterinario",
            password="testpass123",
            email="vet@example.com",
            first_name="Vet",
            last_name="Demo",
        )
        cls.veterinario.groups.add(cls.group)
        cls.veterinario.user_permissions.set(permissions)

        cls.cliente = Cliente.objects.create(
            rut=11111111,
            nombre_cliente="Cliente Panel",
            direccion="Calle Falsa 123",
            telefono="+56911111111",
            email="cliente.panel@example.com",
        )
        cls.mascota = Mascota.objects.create(
            nombre="Rocky",
            numero_chip=5555555555555,
            especie="Perro",
            raza="Mestizo",
            fecha_nacimiento=timezone.now().date(),
            cliente=cls.cliente,
            historial_medico="",
        )
        cls.existing_cita = Cita.objects.create(
            cliente=cls.cliente,
            mascota=cls.mascota,
            estado='1',
            usuario=cls.veterinario,
            fecha=timezone.now() + timedelta(days=2),
            servicio='general',
        )

    def setUp(self):
        self.client.force_login(self.veterinario)

    def test_crear_cita_mediante_formulario(self):
        payload = {
            "servicio": "general",
            "estado": "0",
            "usuario": self.veterinario.pk,
            "fecha": (timezone.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M"),
        }

        response = self.client.post(reverse("panel_cita_nuevo"), data=payload)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("panel_cita_listar"))
        self.assertTrue(
            Cita.objects.filter(usuario=self.veterinario, estado='0', servicio="general").exists()
        )

    def test_editar_cita_actualiza_campos(self):
        new_datetime = (timezone.now() + timedelta(days=3)).strftime("%Y-%m-%dT%H:%M")
        response = self.client.post(
            reverse("panel_cita_editar", args=[self.existing_cita.n_cita]),
            data={
                "cliente": self.cliente.pk,
                "mascota": self.mascota.pk,
                "servicio": "dentista",
                "estado": "1",
                "usuario": self.veterinario.pk,
                "fecha": new_datetime,
                "asistencia": "P",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("panel_cita_listar"))

        self.existing_cita.refresh_from_db()
        self.assertEqual(self.existing_cita.servicio, "dentista")
        self.assertEqual(self.existing_cita.usuario, self.veterinario)