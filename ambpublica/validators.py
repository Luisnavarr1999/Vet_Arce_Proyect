import re
from typing import Tuple
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# Si igual quieres restringir el rango, déjalo opcional
ENFORCE_REALISTIC_RANGE = False
RUT_REALISTIC_MIN = 1_000_000
RUT_REALISTIC_MAX = 25_000_000


def compute_dv(number: int) -> str:
    """Calcula el dígito verificador usando el módulo 11."""
    seq = (2, 3, 4, 5, 6, 7)
    s, i = 0, 0
    for d in reversed(str(number)):
        s += int(d) * seq[i % len(seq)]
        i += 1
    r = 11 - (s % 11)
    return "0" if r == 11 else "K" if r == 10 else str(r)


def format_rut(number: int, dv: str) -> str:
    """Devuelve el RUT formateado con puntos y guion (ej: 12.345.678-5)."""
    cuerpo = f"{number:,}".replace(",", ".")
    return f"{cuerpo}-{dv}"


def parse_and_validate_rut(value: str) -> Tuple[int, str]:
    """Valida la estructura y el dígito verificador del RUT."""
    if value is None:
        raise ValidationError(_("Debe ingresar un RUT."))

    cleaned = re.sub(r"[^0-9kK]", "", str(value)).upper()
    if len(cleaned) < 2:
        raise ValidationError(_("Ingrese un RUT con dígito verificador."))

    body, dv = cleaned[:-1], cleaned[-1]
    if not body.isdigit():
        raise ValidationError(_("El RUT solo puede contener números antes del dígito verificador."))
    if dv not in "0123456789K":
        raise ValidationError(_("El dígito verificador debe ser un número o la letra K."))

    number = int(body)
    if ENFORCE_REALISTIC_RANGE and not (RUT_REALISTIC_MIN <= number <= RUT_REALISTIC_MAX):
        raise ValidationError(_("Ingrese un RUT válido."))

    if compute_dv(number) != dv:
        raise ValidationError(_("El dígito verificador no es válido."))

    return number, dv


def normalize_rut(value: str) -> Tuple[int, str]:
    """
    Limpia y normaliza el RUT ingresado.
    Retorna:
      - el número entero (para guardar en BD)
      - el RUT formateado con puntos y guion (para mostrar)
    """
    cleaned = re.sub(r"[^0-9kK]", "", str(value)).upper()

    if not cleaned:
        raise ValidationError(_("Debe ingresar un RUT."))

    # Si el usuario ingresa solo el cuerpo numérico (sin DV), calculamos el DV.
    if cleaned.isdigit():
        # Para compatibilidad, si viene más largo que el cuerpo típico asumimos que
        # el último dígito corresponde al DV y validamos.
        if len(cleaned) > 8:
            body, dv = cleaned[:-1], cleaned[-1]
            if not body.isdigit():
                raise ValidationError(_("El RUT solo puede contener números antes del dígito verificador."))
            number = int(body)
            if compute_dv(number) != dv:
                raise ValidationError(_("El dígito verificador no es válido."))
        else:
            number = int(cleaned)
            dv = compute_dv(number)
    else:
        number, dv = parse_and_validate_rut(cleaned)

    return number, format_rut(number, dv)
