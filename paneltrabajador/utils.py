"""Utility helpers for the worker panel application."""

from __future__ import annotations

from typing import Any

from django.contrib.auth.models import AbstractBaseUser


def user_is_gerente(user: Any) -> bool:
    """Return ``True`` when the given user belongs to the "gerente" group."""

    if not isinstance(user, AbstractBaseUser):
        return False

    if not user.is_authenticated:
        return False

    return user.groups.filter(name="gerente").exists()