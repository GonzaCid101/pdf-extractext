"""Ports: contratos que los casos de uso necesitan de la persistencia."""
from typing import Protocol

class PDFRepositoryPort(Protocol):
    async def save(self, document: dict) -> str: ...