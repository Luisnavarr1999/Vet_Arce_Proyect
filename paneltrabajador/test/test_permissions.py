from django.contrib.auth.models import Group
from django.test import TestCase

from paneltrabajador.permissions import ROLE_DEFINITIONS, ensure_default_groups


class PermissionSetupTests(TestCase):
    def test_groups_created_with_expected_permissions(self):
        ensure_default_groups()

        for role in ROLE_DEFINITIONS:
            group = Group.objects.get(name=role.name)
            assigned = set(group.permissions.values_list('codename', flat=True))
            self.assertTrue(
                set(role.permissions).issubset(assigned),
                msg=f"Faltan permisos para el grupo {role.name}",
            )