"""Reglas de validación del archivo entrante.

Contiene únicamente reglas de negocio. La lectura por chunks es una estrategia
técnica y por eso vive en la capa API, no en la política.
"""

from dataclasses import dataclass

__all__ = [
    "EmptyFileError",
    "FileTooLargeError",
    "InvalidFileExtensionError",
    "UploadPolicy",
]


class InvalidFileExtensionError(Exception):
    """La extensión del archivo no está permitida."""


class FileTooLargeError(Exception):
    """El archivo excede el tamaño máximo permitido."""


class EmptyFileError(Exception):
    """El archivo no contiene datos."""


@dataclass(frozen=True)
class UploadPolicy:
    allowed_extension: str
    max_size_mb: int

    @property
    def max_size_bytes(self) -> int:
        """Límite en bytes: lo consume el guard técnico de streaming."""
        return self.max_size_mb * 1024 * 1024

    def validate(self, filename: str | None, size_bytes: int) -> None:
        self._validate_extension(filename)
        self._validate_size(size_bytes)
        self._validate_not_empty(size_bytes)

    def _validate_extension(self, filename: str | None) -> None:
        if filename is None or not filename.lower().endswith(
            self.allowed_extension.lower()
        ):
            raise InvalidFileExtensionError(
                f"Solo se permiten archivos {self.allowed_extension.lstrip('.').upper()}"
            )

    def _validate_size(self, size_bytes: int) -> None:
        if size_bytes > self.max_size_bytes:
            raise FileTooLargeError(
                f"El archivo supera el límite máximo de {self.max_size_mb} MB"
            )

    def _validate_not_empty(self, size_bytes: int) -> None:
        if size_bytes <= 0:
            raise EmptyFileError("El archivo está vacío")
