"""Tests unitarios de la política de upload, independientes de HTTP."""

import pytest

from app.services.upload_policy import (
    EmptyFileError,
    FileTooLargeError,
    InvalidFileExtensionError,
    UploadPolicy,
)

MAX_SIZE_MB = 50


@pytest.fixture
def policy() -> UploadPolicy:
    return UploadPolicy(allowed_extension=".pdf", max_size_mb=MAX_SIZE_MB)


class TestArchivoValido:
    def test_valid_file_satisfies_every_rule(self, policy: UploadPolicy) -> None:
        policy.validate_extension("documento.pdf")
        policy.validate_size(size_bytes=1024)
        policy.validate_not_empty(size_bytes=1024)


class TestValidacionDeExtension:
    def test_accepts_pdf_file(self, policy: UploadPolicy) -> None:
        policy.validate_extension("documento.pdf")

    def test_accepts_extension_in_uppercase(self, policy: UploadPolicy) -> None:
        policy.validate_extension("DOCUMENTO.PDF")

    def test_rejects_not_allowed_extension(self, policy: UploadPolicy) -> None:
        with pytest.raises(InvalidFileExtensionError):
            policy.validate_extension("documento.txt")

    def test_rejects_extension_without_separator(self, policy: UploadPolicy) -> None:
        with pytest.raises(InvalidFileExtensionError):
            policy.validate_extension("documentopdf")

    def test_rejects_double_extension(self, policy: UploadPolicy) -> None:
        with pytest.raises(InvalidFileExtensionError):
            policy.validate_extension("documento.pdf.exe")

    def test_rejects_missing_filename(self, policy: UploadPolicy) -> None:
        with pytest.raises(InvalidFileExtensionError):
            policy.validate_extension(None)

    def test_rejects_empty_filename(self, policy: UploadPolicy) -> None:
        with pytest.raises(InvalidFileExtensionError):
            policy.validate_extension("")


class TestValidacionDeTamano:
    def test_accepts_file_within_limit(self, policy: UploadPolicy) -> None:
        policy.validate_size(size_bytes=1024)

    def test_accepts_file_at_max_size(self, policy: UploadPolicy) -> None:
        policy.validate_size(size_bytes=policy.max_size_bytes)

    def test_rejects_file_over_max_size(self, policy: UploadPolicy) -> None:
        with pytest.raises(FileTooLargeError):
            policy.validate_size(size_bytes=policy.max_size_bytes + 1)


class TestValidacionDeArchivoVacio:
    def test_accepts_non_empty_file(self, policy: UploadPolicy) -> None:
        policy.validate_not_empty(size_bytes=1)

    def test_rejects_empty_file(self, policy: UploadPolicy) -> None:
        with pytest.raises(EmptyFileError):
            policy.validate_not_empty(size_bytes=0)

    def test_rejects_negative_size(self, policy: UploadPolicy) -> None:
        with pytest.raises(EmptyFileError):
            policy.validate_not_empty(size_bytes=-1)


class TestConfiguracion:
    def test_custom_max_size_defines_the_limit_in_bytes(self) -> None:
        policy = UploadPolicy(allowed_extension=".pdf", max_size_mb=10)

        assert policy.max_size_bytes == 10 * 1024 * 1024

    def test_accepts_file_at_custom_max_size(self) -> None:
        policy = UploadPolicy(allowed_extension=".pdf", max_size_mb=10)

        policy.validate_size(size_bytes=10 * 1024 * 1024)

    def test_rejects_file_over_custom_max_size(self) -> None:
        policy = UploadPolicy(allowed_extension=".pdf", max_size_mb=10)

        with pytest.raises(FileTooLargeError):
            policy.validate_size(size_bytes=10 * 1024 * 1024 + 1)

    def test_custom_max_size_is_reflected_in_the_error_message(self) -> None:
        policy = UploadPolicy(allowed_extension=".pdf", max_size_mb=10)

        with pytest.raises(FileTooLargeError) as error:
            policy.validate_size(size_bytes=10 * 1024 * 1024 + 1)

        assert str(error.value) == "El archivo supera el límite máximo de 10 MB"

    def test_custom_extension_is_the_only_allowed_one(self) -> None:
        policy = UploadPolicy(allowed_extension=".png", max_size_mb=MAX_SIZE_MB)

        policy.validate_extension("imagen.png")

        with pytest.raises(InvalidFileExtensionError):
            policy.validate_extension("documento.pdf")

    def test_custom_extension_is_reflected_in_the_error_message(self) -> None:
        policy = UploadPolicy(allowed_extension=".png", max_size_mb=MAX_SIZE_MB)

        with pytest.raises(InvalidFileExtensionError) as error:
            policy.validate_extension("documento.pdf")

        assert str(error.value) == "Solo se permiten archivos PNG"
