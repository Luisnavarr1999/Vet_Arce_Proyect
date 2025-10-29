from django.contrib import messages
from django.shortcuts import redirect, render

from paneltrabajador.models import ChatConversation


def chat_conversation_list(request):
    """Lista las conversaciones iniciadas desde el chatbot público."""

    if not request.user.is_authenticated:
        return redirect('panel_home')

    if not request.user.has_perm('paneltrabajador.view_chatconversation'):
        messages.error(request, "No tiene los permisos para ver el chat en vivo.")
        return redirect('panel_home')

    pending = ChatConversation.objects.filter(state=ChatConversation.STATE_PENDING)
    active = ChatConversation.objects.filter(state=ChatConversation.STATE_ACTIVE)
    recent_closed = ChatConversation.objects.filter(state=ChatConversation.STATE_CLOSED)[:10]

    context = {
        'pending': pending,
        'active': active,
        'recent_closed': recent_closed,
    }
    return render(request, 'paneltrabajador/chat/listado.html', context)