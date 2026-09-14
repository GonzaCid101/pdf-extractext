"""Implementaciones falsas (in-memory) para tests de servicios.
"""

from app.repository.pdf_repository import DuplicateRecordError


class FakePDFRepository:

    def __init__(self) -> None:
        self._documents: dict[str, dict] = {}

    async def save(self, document: dict) -> str:
        if any(
            doc["checksum"] == document["checksum"] for doc in self._documents.values()
        ):
            raise DuplicateRecordError("Document with same checksum already exists")
        new_id = f"fake-id-{len(self._documents) + 1}"
        self._documents[new_id] = document
        return new_id
