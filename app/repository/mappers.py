"""Traducción entre documentos de MongoDB y entidades de dominio."""

from bson import ObjectId

from app.domain.pdf_document import PDFDocument


def mongo_to_domain(mongo_doc: dict) -> PDFDocument:
    return PDFDocument(
        id=str(mongo_doc["_id"]),
        filename=mongo_doc["filename"],
        extracted_text=mongo_doc["extracted_text"],
        checksum=mongo_doc["checksum"],
    )


def domain_to_mongo(entity: PDFDocument) -> dict:
    mongo_doc = {
        "filename": entity.filename,
        "extracted_text": entity.extracted_text,
        "checksum": entity.checksum,
    }

    # Un id vacío indica un documento nuevo; MongoDB generará el _id
    if entity.id:
        mongo_doc["_id"] = ObjectId(entity.id)

    return mongo_doc
