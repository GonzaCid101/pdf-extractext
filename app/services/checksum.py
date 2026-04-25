"""Servicio de cálculo de checksums."""

import hashlib


def generate_checksum(content: bytes) -> str:
    """Genera SHA-256 hash de bytes."""
    return hashlib.sha256(content).hexdigest()
