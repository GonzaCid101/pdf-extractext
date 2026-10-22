"""Adapter HTTP de la subida de PDFs."""

from fastapi import APIRouter, Depends, File, UploadFile, status

from app.api.dependencies import get_pdf_service, get_upload_policy
from app.api.mappers import to_pdf_document_response
from app.api.upload_reader import read_upload
from app.exceptions.rfc9457 import (
    EmptyFileException,
    FilenameTooLongException,
    FileTooLargeException,
    InvalidFileExtensionException,
    InvalidPDFContentException,
)
from app.models.pdf_models import PDFDocumentResponse
from app.services.pdf_service import FilenameTooLongError, PDFService
from app.services.upload_policy import (
    EmptyFileError,
    FileTooLargeError,
    InvalidFileExtensionError,
    UploadPolicy,
)

router = APIRouter()


@router.post(
    "/upload-pdf",
    response_model=PDFDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_pdf(
    file: UploadFile = File(...),
    service: PDFService = Depends(get_pdf_service),
    policy: UploadPolicy = Depends(get_upload_policy),
) -> PDFDocumentResponse:
    try:
        policy.validate_extension(file.filename)
        content, checksum = await read_upload(file, policy)
        policy.validate_not_empty(len(content))
        document = await service.process_and_save(
            file.filename, content, checksum=checksum
        )
    except InvalidFileExtensionError as error:
        raise InvalidFileExtensionException(detail=str(error)) from error
    except FileTooLargeError as error:
        raise FileTooLargeException(detail=str(error)) from error
    except EmptyFileError as error:
        raise EmptyFileException(detail=str(error)) from error
    except FilenameTooLongError as error:
        raise FilenameTooLongException(detail=str(error)) from error
    except ValueError as error:
        raise InvalidPDFContentException(detail=str(error)) from error

    return to_pdf_document_response(document)
