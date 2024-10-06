from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

# Comando personalizado para la configuración rápida de los permisos y grupos
# Ya creados de Django Auth
class Command(BaseCommand):

    PERMISOS_GERENTE = ["add_user", "change_user", "delete_user", "view_user", "add_cita", "change_cita", "delete_cita", "view_cita", "add_cliente", "change_cliente", "delete_cliente", "view_cliente", "add_factura", "change_factura",
                        "delete_factura", "view_factura", "add_mascota", "change_mascota", "delete_mascota", "view_mascota", "add_producto", "change_producto", "delete_producto", "view_producto"]

    PERMISOS_VET = ["view_user", "change_cita", "view_cita", "view_cliente", "change_mascota", "view_mascota", "view_producto"]
    PERMISOS_RECEP = ["view_user", "add_cita", "change_cita", "delete_cita", "view_cita", "add_cliente", "change_cliente", "view_cliente", "add_factura", "change_factura",
                      "view_factura", "add_mascota", "change_mascota", "delete_mascota", "view_mascota", "change_producto", "view_producto"]

    def handle(self, **options):

        print("..::PROCESO INICIAL DE PERMISOS Y GRUPOS POR PERICODERS::..")

        print("Lista de permisos disponibles: ", end="")

        for action in Permission.objects.all():
            print("\"{}\",".format(action.codename), end="")

        print("\nCreación de grupos")

        veterinario_group, created = Group.objects.get_or_create(name='veterinario')
        gerente_group, created = Group.objects.get_or_create(name='gerente')
        recepcionista_group, created = Group.objects.get_or_create(name='recepcionista')

        print("OK")

        print("Limpieza de permisos en caso de que existieran")

        gerente_group.permissions.clear()
        veterinario_group.permissions.clear()
        recepcionista_group.permissions.clear()

        print("OK")

        print("Asignacion permisos GERENTE")
        for permiso in self.PERMISOS_GERENTE:
            perm = Permission.objects.get(codename=permiso)
            gerente_group.permissions.add(perm)

        print("OK")

        print("Asignacion permisos VETERINARIO")

        for permiso in self.PERMISOS_VET:
            perm = Permission.objects.get(codename=permiso)
            veterinario_group.permissions.add(perm)

        print("OK")

        print("Asignacion permisos RECEPCIONISTA")

        for permiso in self.PERMISOS_RECEP:
            perm = Permission.objects.get(codename=permiso)
            recepcionista_group.permissions.add(perm)

        print("OK")

        print("TODO OK PROCESO FINALIZADO")
