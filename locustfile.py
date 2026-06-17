from locust import HttpUser, task, between
import random
import io


class PDFUser(HttpUser):
    wait_time = between(1, 3)

    def _generate_pdf(self) -> bytes:
        return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids []\n/Count 0\n>>\nendobj\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF"

    @task(3)
    def get_pdfs(self):
        self.client.get("/pdfs")

    @task(1)
    def upload_pdf(self):
        pdf_bytes = self._generate_pdf()
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
