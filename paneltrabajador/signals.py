from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .permissions import ensure_default_groups


@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    if sender.label != 'paneltrabajador':
        return
    ensure_default_groups()