"""Pruebas de carga con Locust contra la API de PDFs."""

import io
import random
from pathlib import Path

from locust import HttpUser, between, task

DUMMY_PDF_PATH = Path("fixtures/dummy.pdf")


class PDFUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def get_pdfs(self):
        self.client.get("/pdfs")

    @task(1)
    def upload_pdf(self):
        pdf_bytes = DUMMY_PDF_PATH.read_bytes()
        files = {"file": ("test.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
        self.client.post("/upload-pdf", files=files)

    @task(1)
    def get_pdf_by_id(self):
        response = self.client.get("/pdfs")
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list) and len(data) > 0:
                pdf_id = random.choice(data)["_id"]
                self.client.get(f"/pdfs/{pdf_id}")
