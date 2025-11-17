from django.apps import AppConfig


class PaneltrabajadorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'paneltrabajador'

    def ready(self):
        # Importa señales que sincronizan grupos/permisos después de las migraciones
        from . import signals  # noqa: F401

