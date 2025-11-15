import os
import tempfile
from datetime import timedelta
from unittest import mock

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.test import TestCase, override_settings
from django.utils import timezone

from paneltrabajador.models import (
    ChatConversation,
    ChatMessage,
    Cita,
    Cliente,
    Mascota,
    MascotaDocumento,
    UserProfile,
)


class BaseModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="veterinario", email="vet@example.com", password="secret"
        )
        self.cliente = Cliente.objects.create(
            rut=12345678,
            nombre_cliente="Cliente",
            direccion="Calle 123",
            telefono="+56912345678",
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


class CitaModelTests(BaseModelTest):
    def test_manager_updates_past_available_slots(self):
        past = timezone.now() - timedelta(days=1)
        cita = Cita.objects.create(
            estado="0",
            usuario=self.user,
            fecha=past,
            servicio="general",
        )
        refreshed = Cita.objects.get(pk=cita.pk)
        self.assertEqual(refreshed.estado, "3")
        self.assertIsNone(refreshed.asistencia)

    def test_save_resets_asistencia_for_cancelled(self):
        cita = Cita.objects.create(
            estado="1",
            usuario=self.user,
            fecha=timezone.now() + timedelta(days=1),
            servicio="general",
        )
        cita.asistencia = "A"
        cita.estado = "2"
        cita.save(update_fields=["estado"])
        cita.refresh_from_db()
        self.assertIsNone(cita.asistencia)

    def test_save_sets_default_asistencia_when_reserved(self):
        cita = Cita(
            estado="1",
            usuario=self.user,
            fecha=timezone.now() + timedelta(days=1),
            servicio="general",
        )
        cita.asistencia = None
        cita.save()
        self.assertEqual(cita.asistencia, "P")


class MascotaDocumentoTests(BaseModelTest):
    def test_delete_removes_file_from_storage(self):
        with tempfile.TemporaryDirectory() as tmpdir, override_settings(MEDIA_ROOT=tmpdir):
            documento = MascotaDocumento.objects.create(
                mascota=self.mascota,
                archivo=ContentFile(b"data", name="doc.txt"),
            )
            path = documento.archivo.path
            self.assertTrue(os.path.exists(path))
            documento.delete()
            self.assertFalse(os.path.exists(path))


class ChatMessageTests(BaseModelTest):
    def test_new_message_touches_conversation(self):
        conversation = ChatConversation.objects.create()
        with mock.patch.object(conversation, "touch") as mocked_touch:
            message = ChatMessage(conversation=conversation, author=ChatMessage.AUTHOR_BOT, content="Hola")
            message.save()
        mocked_touch.assert_called_once()
        args, kwargs = mocked_touch.call_args
        self.assertIn("Hola", kwargs["summary"] if "summary" in kwargs else args[0])


class UserProfileTests(BaseModelTest):
    def test_replace_photo_deletes_previous_file(self):
        with tempfile.TemporaryDirectory() as tmpdir, override_settings(MEDIA_ROOT=tmpdir):
            profile = UserProfile.objects.create(user=self.user)
            profile.photo.save("first.jpg", ContentFile(b"old"))
            first_path = profile.photo.path
            self.assertTrue(os.path.exists(first_path))

            profile.photo.save("second.jpg", ContentFile(b"new"))
            second_path = profile.photo.path
            self.assertTrue(os.path.exists(second_path))
            self.assertFalse(os.path.exists(first_path))

    def test_delete_removes_file(self):
        with tempfile.TemporaryDirectory() as tmpdir, override_settings(MEDIA_ROOT=tmpdir):
            profile = UserProfile.objects.create(user=self.user)
            profile.photo.save("photo.jpg", ContentFile(b"content"))
            path = profile.photo.path
            self.assertTrue(os.path.exists(path))
            profile.delete()
            self.assertFalse(os.path.exists(path))