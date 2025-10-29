from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from paneltrabajador.models import ChatConversation, ChatMessage


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


def chat_conversation_detail(request, conversation_id):
    """Muestra y permite responder una conversación específica."""

    if not request.user.is_authenticated:
        return redirect('panel_home')

    if not request.user.has_perm('paneltrabajador.view_chatconversation'):
        messages.error(request, "No tiene los permisos para ver el chat en vivo.")
        return redirect('panel_home')

    conversation = get_object_or_404(ChatConversation, pk=conversation_id)

    # Si el usuario aún no ha tomado la conversación, la marcamos como activa.
    if conversation.state == ChatConversation.STATE_PENDING:
        conversation.state = ChatConversation.STATE_ACTIVE
        conversation.assigned_to = conversation.assigned_to or request.user
        conversation.updated_at = timezone.now()
        conversation.save(update_fields=['state', 'assigned_to', 'updated_at'])

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'send':
            if conversation.state == ChatConversation.STATE_CLOSED:
                messages.error(request, "La conversación ya está cerrada. No puedes enviar nuevos mensajes.")
                return redirect('panel_chat_detail', conversation_id=conversation.id)
            message = (request.POST.get('message') or '').strip()
            if message:
                ChatMessage.objects.create(
                    conversation=conversation,
                    author=ChatMessage.AUTHOR_STAFF,
                    content=message,
                    staff_user=request.user,
                )
                if conversation.assigned_to_id is None:
                    conversation.assigned_to = request.user
                    conversation.save(update_fields=['assigned_to'])
            else:
                messages.error(request, "Debes escribir un mensaje para enviarlo.")
            return redirect('panel_chat_detail', conversation_id=conversation.id)

        if action == 'close':
            conversation.state = ChatConversation.STATE_CLOSED
            if conversation.assigned_to_id is None:
                conversation.assigned_to = request.user
            conversation.save(update_fields=['state', 'assigned_to'])
            messages.success(request, "La conversación fue marcada como cerrada.")
            return redirect('panel_chat_detail', conversation_id=conversation.id)

    messages_qs = conversation.messages.select_related('staff_user')

    context = {
        'conversation': conversation,
        'messages': messages_qs,
    }
    return render(request, 'paneltrabajador/chat/detalle.html', context)


@require_http_methods(["GET"])
def chat_conversation_messages(request, conversation_id):
    """Entrega los mensajes de una conversación en formato JSON para el panel."""

    if not request.user.is_authenticated or not request.user.has_perm('paneltrabajador.view_chatconversation'):
        return JsonResponse({'error': 'No autorizado'}, status=403)

    conversation = get_object_or_404(ChatConversation, pk=conversation_id)

    messages_payload = []
    last_id = None

    for message in conversation.messages.select_related('staff_user').all():
        last_id = message.id
        messages_payload.append(
            {
                'id': message.id,
                'author': message.author,
                'content': message.content,
                'created_at': message.created_at.isoformat(),
                'staff_user': message.staff_user.username if message.staff_user else None,
            }
        )

    return JsonResponse(
        {
            'conversation': {
                'id': conversation.id,
                'state': conversation.state,
                'assigned_to': conversation.assigned_to.get_full_name() if conversation.assigned_to else None,
                'last_message_at': conversation.last_message_at.isoformat(),
            },
            'messages': messages_payload,
            'last_id': last_id,
        }
    )