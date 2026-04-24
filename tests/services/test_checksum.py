"""Tests para el servicio de cálculo de checksum."""

import pytest

from app.services.checksum import generate_checksum


class TestGenerateChecksum:
    """Tests para la función generate_checksum."""

    def test_mismos_bytes_producen_mismo_hash(self):
        content = b"contenido de prueba"
        hash1 = generate_checksum(content)
        hash2 = generate_checksum(content)

        assert hash1 == hash2

    def test_distintos_bytes_producen_distinto_hash(self):
        content_a = b"contenido A"
        content_b = b"contenido B"
        hash_a = generate_checksum(content_a)
        hash_b = generate_checksum(content_b)

        assert hash_a != hash_b

    def test_retorna_string_hexadecimal(self):
        content = b"cualquier contenido"
        result = generate_checksum(content)

        assert isinstance(result, str)

        # Verifica que es hexadecimal (solo caracteres 0-9 y a-f)
        assert all(c in "0123456789abcdef" for c in result.lower())
