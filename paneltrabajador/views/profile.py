"""Vistas relacionadas con el perfil del colaborador."""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import redirect, render

from paneltrabajador.forms import (
    StyledPasswordChangeForm,
    UserProfileAvatarForm,
    UserProfileForm,
)
from paneltrabajador.models import UserProfile


def perfil(request):
    """Permite a los colaboradores administrar la información de su perfil."""

    if not request.user.is_authenticated:
        return redirect("panel_home")

    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    username_form = UserProfileForm(instance=request.user)
    avatar_form = UserProfileAvatarForm(instance=profile)
    password_form = StyledPasswordChangeForm(user=request.user)

    if request.method == "POST":
        form_type = request.POST.get("form_type", "").strip()

        if form_type == "username":
            username_form = UserProfileForm(request.POST, instance=request.user)
            if username_form.is_valid():
                username_form.save()
                messages.success(request, "Tu nombre de usuario se ha actualizado correctamente.")
                return redirect("panel_perfil")
            messages.error(request, "No fue posible actualizar tu nombre de usuario. Revisa los campos resaltados.")

        elif form_type == "avatar":
            avatar_form = UserProfileAvatarForm(request.POST, request.FILES, instance=profile)
            if avatar_form.is_valid():
                profile = avatar_form.save()
                if profile.photo:
                    messages.success(request, "Se actualizó tu fotografía de perfil.")
                else:
                    messages.success(request, "Se eliminó la fotografía de perfil.")
                return redirect("panel_perfil")
            messages.error(request, "No pudimos procesar la fotografía. Por favor, intenta nuevamente.")

        elif form_type == "password":
            password_form = StyledPasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Tu contraseña se cambió correctamente.")
                return redirect("panel_perfil")
            messages.error(request, "Revisa los datos ingresados para cambiar tu contraseña.")

        else:
            messages.error(request, "No se reconoció la acción solicitada.")

    context = {
        "profile": profile,
        "username_form": username_form,
        "avatar_form": avatar_form,
        "password_form": password_form,
    }
    return render(request, "paneltrabajador/perfil.html", context)