"""Tests para servicio de checksum."""

from app.services.checksum import ChecksumService


class TestChecksumService:
    """Tests para ChecksumService."""

    def test_same_bytes_produce_same_hash(self, sample_text_bytes):
        service = ChecksumService()
        hash1 = service.generate(sample_text_bytes)
        hash2 = service.generate(sample_text_bytes)

        assert hash1 == hash2

    def test_different_bytes_produce_different_hash(self, sample_text_bytes):
        service = ChecksumService()
        hash_a = service.generate(sample_text_bytes)
        hash_b = service.generate(b"otro contenido")

        assert hash_a != hash_b

    def test_returns_hexadecimal_string(self, sample_text_bytes):
        service = ChecksumService()
        result = service.generate(sample_text_bytes)

        assert isinstance(result, str)
        assert all(c in "0123456789abcdef" for c in result.lower())
