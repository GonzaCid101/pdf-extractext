"""Tests para los mappers de MongoDB a dominio y viceversa."""

from bson import ObjectId

from app.domain.pdf_document import PDFDocument
from app.repository.mappers import domain_to_mongo, mongo_to_domain


class TestMongoToDomain:

    def test_converts_mongo_document_with_objectid(self):
        mongo_doc = {
            "_id": ObjectId("65f1a2b3c4d5e6f7a8b9c0d1"),
            "filename": "informe.pdf",
            "extracted_text": "Contenido extraido",
            "checksum": "a" * 64,
        }

        document = mongo_to_domain(mongo_doc)

        assert isinstance(document, PDFDocument)
        assert document.id == "65f1a2b3c4d5e6f7a8b9c0d1"
        assert isinstance(document.id, str)
        assert document.filename == "informe.pdf"
        assert document.extracted_text == "Contenido extraido"
        assert document.checksum == "a" * 64


class TestDomainToMongo:

    def test_converts_entity_with_id(self):
        entity = PDFDocument(
            id="65f1a2b3c4d5e6f7a8b9c0d1",
            filename="informe.pdf",
            extracted_text="Contenido extraido",
            checksum="a" * 64,
        )

        mongo_doc = domain_to_mongo(entity)

        assert mongo_doc["_id"] == ObjectId("65f1a2b3c4d5e6f7a8b9c0d1")
        assert isinstance(mongo_doc["_id"], ObjectId)
        assert mongo_doc["filename"] == "informe.pdf"
        assert mongo_doc["extracted_text"] == "Contenido extraido"
        assert mongo_doc["checksum"] == "a" * 64

    def test_omits_id_when_empty_for_insert(self):
        entity = PDFDocument(
            id="",
            filename="nuevo.pdf",
            extracted_text="Documento nuevo",
            checksum="b" * 64,
        )

        mongo_doc = domain_to_mongo(entity)

        assert "_id" not in mongo_doc
        assert mongo_doc["filename"] == "nuevo.pdf"
        assert mongo_doc["checksum"] == "b" * 64

    def test_roundtrip_preserves_data(self):
        mongo_doc = {
            "_id": ObjectId(),
            "filename": "viaje_de_ida_y_vuelta.pdf",
            "extracted_text": "Texto",
            "checksum": "c" * 64,
        }

        entity = mongo_to_domain(mongo_doc)
        result = domain_to_mongo(entity)

        assert result == mongo_doc
