"""Servicio para cálculo de checksums."""

import hashlib


def generate_checksum(content: bytes) -> str:
    """Genera un checksum SHA-256 del contenido dado."""
    return hashlib.sha256(content).hexdigest()
