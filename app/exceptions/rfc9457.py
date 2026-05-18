"""Implementación de excepciones basadas en RFC 9457 (Problem Details for HTTP APIs)."""

from typing import Any

from fastapi import status


class RFC9457Exception(Exception):
    """Excepción base siguiendo el estándar RFC 9457."""

    def __init__(
        self,
        *,
        type_: str,
        title: str,
        status: int,
        detail: str,
        instance: str,
        **kwargs: Any,
    ) -> None:
        self.type = type_
        self.title = title
        self.status = status
        self.detail = detail
        self.instance = instance
        self._extra = kwargs

    def to_dict(self) -> dict:
        result = {
            "type": self.type,
            "title": self.title,
            "status": self.status,
            "detail": self.detail,
            "instance": self.instance,
        }
        result.update(self._extra)
        return result


class DuplicatePDFException(RFC9457Exception):
    """Excepción para PDF duplicado detectado por checksum."""

    def __init__(self, detail: str = "El documento ya existe en el sistema") -> None:
        super().__init__(
            type_="urn:pdf-extractext:errors:duplicate-pdf",
            title="Documento PDF duplicado",
            status=status.HTTP_409_CONFLICT,
            detail=detail,
            instance="/upload-pdf",
        )
