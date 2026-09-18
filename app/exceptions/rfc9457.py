# FASE GREEN: Implementación mínima para pasar el test
"""Implementación de excepciones basadas en RFC 9457 (Problem Details for HTTP APIs).

Regla de Oro: cero acoplamiento web. Solo transporta información del problema;
la conversión a respuestas HTTP es responsabilidad de los exception handlers
en la capa de API.
"""

from http import HTTPStatus
from typing import Any


class RFC9457Exception(Exception):

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

    def __init__(
        self,
        detail: str = "El documento ya existe en el sistema",
        instance: str = "/upload-pdf",
    ) -> None:
        super().__init__(
            type_="urn:pdf-extractext:errors:duplicate-pdf",
            title="Documento PDF duplicado",
            status=HTTPStatus.CONFLICT,
            detail=detail,
            instance=instance,
        )


class InvalidObjectIdException(RFC9457Exception):

    def __init__(
        self,
        instance: str,
        detail: str = "El identificador proporcionado no es un ObjectId válido",
    ) -> None:
        super().__init__(
            type_="urn:pdf-extractext:errors:invalid-object-id",
            title="ObjectId malformado",
            status=HTTPStatus.BAD_REQUEST,
            detail=detail,
            instance=instance,
        )
