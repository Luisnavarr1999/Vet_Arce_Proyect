import re
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _

CONTROL_CHAR_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def _normalize_whitespace(value: str, allow_newlines: bool) -> str:
    if allow_newlines:
        # Mantiene saltos de línea pero colapsa espacios redundantes
        value = re.sub(r"[ \t]+", " ", value)
        # Normaliza finales de línea
        value = value.replace("\r\n", "\n").replace("\r", "\n")
        # Limita secuencias muy largas de saltos a dos
        value = re.sub(r"\n{3,}", "\n\n", value)
    else:
        value = re.sub(r"\s+", " ", value)
    return value.strip()


def clean_plain_text(value: str, *, max_length: int = 255, field_name: str | None = None) -> str:
    """Normaliza texto de un solo renglón y valida longitud/caracteres peligrosos."""
    label = field_name or _("este campo")
    text = strip_tags(value or "")
    text = _normalize_whitespace(text, allow_newlines=False)

    if not text:
        raise ValidationError(_("%(field)s no puede estar vacío."), params={"field": label})

    if CONTROL_CHAR_PATTERN.search(text):
        raise ValidationError(_("%(field)s contiene caracteres no permitidos."), params={"field": label})

    if len(text) > max_length:
        raise ValidationError(
            _("%(field)s no puede superar %(max)d caracteres."),
            params={"field": label, "max": max_length},
        )

    return text


def clean_multiline_text(value: str, *, max_length: int = 2000, field_name: str | None = None) -> str:
    """Sanitiza texto largo permitiendo saltos de línea controlados."""
    label = field_name or _("este campo")
    text = strip_tags(value or "")
    text = _normalize_whitespace(text, allow_newlines=True)

    if not text:
        raise ValidationError(_("%(field)s no puede estar vacío."), params={"field": label})

    if CONTROL_CHAR_PATTERN.search(text):
        raise ValidationError(_("%(field)s contiene caracteres no permitidos."), params={"field": label})

    if len(text) > max_length:
        raise ValidationError(
            _("%(field)s no puede superar %(max)d caracteres."),
            params={"field": label, "max": max_length},
        )

    return text