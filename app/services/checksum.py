"""Servicio de cálculo de checksums."""

import hashlib


class ChecksumService:
    def generate(self, content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()
