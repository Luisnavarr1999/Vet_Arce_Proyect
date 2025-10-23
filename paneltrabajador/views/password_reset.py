"""Vistas relacionadas con el flujo de reseteo de contraseña del panel."""
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from paneltrabajador.forms import PasswordResetRequestForm

class PanelPasswordResetView(PasswordResetView):
    form_class = PasswordResetRequestForm
    template_name = "paneltrabajador/password_reset_form.html"

    # asunto + cuerpo (texto y HTML)
    subject_template_name = "paneltrabajador/password_reset_subject.txt"
    email_template_name = "paneltrabajador/password_reset_email.txt"        # TEXTO
    html_email_template_name = "paneltrabajador/password_reset_email.html"  # HTML estilo tarjeta

    success_url = reverse_lazy("panel_password_reset_done")
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)

    # 👇 Estos valores estarán disponibles en los templates
    extra_email_context = {
        "site_name": "Veterinaria de Arce",
        "logo_url": "https://i.postimg.cc/x1RJ1G0t/Logovetarce.png",  # usa tu logo público definitivo
        "primary_color": "#1a73e8",
        "website_url": "https://www.veterinariadearce.cl",
        "reply_to": "shadowxd41@gmail.com",  # si quieres usar Reply-To
    }

    def form_valid(self, form):
        messages.success(
            self.request,
            "Hemos enviado un correo con las instrucciones para restablecer la contraseña.",
        )
        return super().form_valid(form)

password_reset_request = PanelPasswordResetView.as_view()
