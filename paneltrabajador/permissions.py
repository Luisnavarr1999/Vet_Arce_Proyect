from __future__ import annotations

from dataclasses import dataclass

from django.contrib.auth.models import Group, Permission


@dataclass(frozen=True)
class RoleDefinition:
    name: str
    permissions: tuple[str, ...]


ROLE_DEFINITIONS = (
    RoleDefinition(
        name='gerente',
        permissions=(
            "add_user",
            "change_user",
            "delete_user",
            "view_user",
            "add_cita",
            "change_cita",
            "delete_cita",
            "view_cita",
            "add_cliente",
            "change_cliente",
            "delete_cliente",
            "view_cliente",
            "add_factura",
            "change_factura",
            "delete_factura",
            "view_factura",
            "add_mascota",
            "change_mascota",
            "delete_mascota",
            "view_mascota",
            "add_producto",
            "change_producto",
            "delete_producto",
            "view_producto",
        ),
    ),
    RoleDefinition(
        name='veterinario',
        permissions=(
            "view_user",
            "view_cita",
            "change_mascota",
            "view_mascota",
            "view_producto",
        ),
    ),
    RoleDefinition(
        name='recepcionista',
        permissions=(
            "view_user",
            "add_cita",
            "change_cita",
            "delete_cita",
            "view_cita",
            "add_cliente",
            "change_cliente",
            "view_cliente",
            "add_factura",
            "change_factura",
            "view_factura",
            "add_mascota",
            "change_mascota",
            "delete_mascota",
            "view_mascota",
            "change_producto",
            "view_producto",
            "view_chatconversation",
            "view_chatmessage",
            "add_chatmessage",
        ),
    ),
)


def ensure_default_groups(stdout=None) -> None:
    """Crea/actualiza los grupos base del panel con sus permisos."""

    for role in ROLE_DEFINITIONS:
        group, _ = Group.objects.get_or_create(name=role.name)
        permissions = Permission.objects.filter(codename__in=role.permissions)
        found = set(permissions.values_list('codename', flat=True))
        missing = set(role.permissions) - found
        if missing:
            raise Permission.DoesNotExist(
                f"No se encontraron los permisos requeridos para {role.name}: {', '.join(sorted(missing))}"
            )
        group.permissions.set(permissions)
        if stdout:
            stdout.write(f"Permisos sincronizados para el grupo '{role.name}'")