"""Utility helpers for the worker panel application."""

from __future__ import annotations

from typing import Any

from django.contrib.auth.models import AbstractBaseUser


def user_is_gerente(user: Any) -> bool:
    """Return ``True`` when the user is superuser or belongs to the "gerente" group."""

    if not isinstance(user, AbstractBaseUser):
        return False

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return user.groups.filter(name="gerente").exists()