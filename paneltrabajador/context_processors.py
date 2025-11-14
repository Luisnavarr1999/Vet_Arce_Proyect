"""Context processors for the worker panel application."""

from __future__ import annotations

from django.contrib.auth.models import AbstractBaseUser
from django.http import HttpRequest

from paneltrabajador.models import ChatConversation
from paneltrabajador.utils import user_is_gerente



def chat_notifications(request: HttpRequest) -> dict[str, int | bool]:
    """Include information about pending chat conversations for staff users."""

    context: dict[str, int | bool] = {
        "chat_pending_count": 0,
        "chat_has_pending": False,
        "is_gerente": False,
    }

    user: AbstractBaseUser = request.user  # type: ignore[assignment]

    if not getattr(user, "is_authenticated", False):
        return context
    
    context["is_gerente"] = user_is_gerente(user)

    if not user.has_perm("paneltrabajador.view_chatconversation"):
        return context

    pending_count = (
        ChatConversation.objects.filter(state=ChatConversation.STATE_PENDING)
        .only("id")
        .count()
    )

    context.update(
        {
            "chat_pending_count": pending_count,
            "chat_has_pending": pending_count > 0,
        }
    )

    return context