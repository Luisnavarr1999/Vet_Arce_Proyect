import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class ComplexPasswordValidator:
    """Exige variedad de caracteres para endurecer contraseñas internas."""

    def validate(self, password: str, user=None) -> None:
        if not password:
            raise ValidationError(self.get_help_text())

        checks = {
            'uppercase': bool(re.search(r"[A-ZÁÉÍÓÚÑÜ]", password)),
            'lowercase': bool(re.search(r"[a-záéíóúñü]", password)),
            'digit': bool(re.search(r"\d", password)),
            'symbol': bool(re.search(r"[^\w\s]", password)),
        }

        if sum(checks.values()) < 3:
            raise ValidationError(self.get_help_text())

    def get_help_text(self) -> str:
        return _(
            "La contraseña debe combinar al menos tres de los siguientes tipos de caracteres: "
            "mayúsculas, minúsculas, números y símbolos."
        )