"""Funciones proveedoras para inyección de dependencias (Depends)."""

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.repository.database import get_database
from app.repository.pdf_repository import PDFRepository
from app.services.checksum import ChecksumService
from app.services.pdf_service import PDFService
from app.services.ports import PDFRepositoryPort
from app.services.upload_policy import UploadPolicy


async def get_pdf_repository(
    client: AsyncIOMotorClient = Depends(get_database),
) -> PDFRepositoryPort:
    return PDFRepository(client)


async def get_pdf_service(
    repository: PDFRepositoryPort = Depends(get_pdf_repository),
) -> PDFService:
    return PDFService(repository, ChecksumService())


def get_upload_policy() -> UploadPolicy:
    return UploadPolicy(
        allowed_extension=settings.ALLOWED_FILE_EXTENSION,
        max_size_mb=settings.MAX_FILE_SIZE_MB,
    )
