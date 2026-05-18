"""Funciones proveedoras para inyección de dependencias (Depends)."""

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient

from app.repository.database import get_database
from app.repository.pdf_repository import PDFRepository
from app.services.checksum import ChecksumService
from app.services.pdf_service import PDFService


async def get_pdf_repository(
    db: AsyncIOMotorClient = Depends(get_database),
) -> PDFRepository:
    return PDFRepository(db)


async def get_pdf_service(
    repository: PDFRepository = Depends(get_pdf_repository),
) -> PDFService:
    return PDFService(repository, ChecksumService())
