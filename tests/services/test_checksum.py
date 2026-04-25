"""Tests para servicio de checksum."""

from app.services.checksum import generate_checksum


class TestGenerateChecksum:
    """Tests para generate_checksum."""

    def test_same_bytes_produce_same_hash(self, sample_text_bytes):
        """Mismos bytes producen mismo hash."""
        hash1 = generate_checksum(sample_text_bytes)
        hash2 = generate_checksum(sample_text_bytes)

        assert hash1 == hash2

    def test_different_bytes_produce_different_hash(self, sample_text_bytes):
        """Diferentes bytes producen diferente hash."""
        hash_a = generate_checksum(sample_text_bytes)
        hash_b = generate_checksum(b"otro contenido")

        assert hash_a != hash_b

    def test_returns_hexadecimal_string(self, sample_text_bytes):
        """Retorna string hexadecimal."""
        result = generate_checksum(sample_text_bytes)

        assert isinstance(result, str)
        assert all(c in "0123456789abcdef" for c in result.lower())
