from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from ambpublica.validators import normalize_rut, parse_and_validate_rut


class ParseAndValidateRutTests(SimpleTestCase):
    def test_accepts_formatted_rut(self):
        number, dv = parse_and_validate_rut("12.345.678-5")
        self.assertEqual(number, 12345678)
        self.assertEqual(dv, "5")

    def test_rejects_incorrect_digit(self):
        with self.assertRaisesMessage(ValidationError, "dígito verificador"):
            parse_and_validate_rut("12.345.678-4")

    def test_rejects_missing_dv(self):
        with self.assertRaisesMessage(ValidationError, "dígito verificador no es válido"):
            parse_and_validate_rut("12345678")


class NormalizeRutTests(SimpleTestCase):
    def test_calculates_digit_when_missing(self):
        number, formatted = normalize_rut("12345678")
        self.assertEqual(number, 12345678)
        self.assertEqual(formatted, "12.345.678-5")

    def test_accepts_digits_with_dv(self):
        number, formatted = normalize_rut("123456785")
        self.assertEqual(number, 12345678)
        self.assertEqual(formatted, "12.345.678-5")

    def test_requires_input(self):
        with self.assertRaisesMessage(ValidationError, "Debe ingresar un RUT"):
            normalize_rut("")