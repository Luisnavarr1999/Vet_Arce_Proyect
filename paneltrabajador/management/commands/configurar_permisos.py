from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand

from paneltrabajador.permissions import ROLE_DEFINITIONS, ensure_default_groups


class Command(BaseCommand):
    help = "Sincroniza los grupos 'gerente', 'veterinario' y 'recepcionista' con sus permisos predefinidos."

    def handle(self, **options):
        self.stdout.write("..::PROCESO INICIAL DE PERMISOS Y GRUPOS POR PERICODERS::..")

        available = ", ".join(
            sorted(Permission.objects.values_list("codename", flat=True))
        )
        self.stdout.write(f"Permisos detectados en el sistema: {available}")

        ensure_default_groups(stdout=self.stdout)

        summary = "; ".join(
            f"{role.name}: {len(role.permissions)} permisos"
            for role in ROLE_DEFINITIONS
        )
        self.stdout.write(f"TODO OK. Resumen -> {summary}")
