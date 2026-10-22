"""Tests unitarios de la política de upload, independientes de HTTP."""

import pytest

# FASE RED: Este test fallará inicialmente
from app.services.upload_policy import (
    EmptyFileError,
    FileTooLargeError,
    InvalidFileExtensionError,
    UploadPolicy,
)


@pytest.fixture
def policy() -> UploadPolicy:
    return UploadPolicy(allowed_extension=".pdf", max_size_mb=50)


class TestUploadPolicy:
    """Reglas de validación del archivo entrante."""

    def test_accepts_valid_pdf_file(self, policy: UploadPolicy) -> None:
        policy.validate("documento.pdf", size_bytes=1024)

    def test_rejects_not_allowed_extension(self, policy: UploadPolicy) -> None:
        with pytest.raises(InvalidFileExtensionError):
            policy.validate("documento.txt", size_bytes=1024)

    def test_rejects_file_over_max_size(self, policy: UploadPolicy) -> None:
        with pytest.raises(FileTooLargeError):
            policy.validate("documento.pdf", size_bytes=policy.max_size_bytes + 1)

    def test_rejects_empty_file(self, policy: UploadPolicy) -> None:
        with pytest.raises(EmptyFileError):
            policy.validate("documento.pdf", size_bytes=0)

    def test_accepts_file_at_max_size(self, policy: UploadPolicy) -> None:
        policy.validate("documento.pdf", size_bytes=policy.max_size_bytes)

    def test_accepts_extension_in_uppercase(self, policy: UploadPolicy) -> None:
        policy.validate("DOCUMENTO.PDF", size_bytes=1024)
