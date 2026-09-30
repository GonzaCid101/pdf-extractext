import http from 'k6/http';
import { Trend } from 'k6/metrics';
import { check } from 'k6';

const statusTrend = new Trend('status_codes');

// 409 es una respuesta válida del sistema (deduplicación), no un fallo HTTP.
http.setResponseCallback(http.expectedStatuses({ min: 200, max: 399 }, 409));

export const options = {
    stages: [
        { duration: '10s', target: 100 },
        { duration: '20s', target: 100 },
        { duration: '10s', target: 0 },
    ],
};

const BASE_URL = 'https://pdf-extractext.universidad.localhost';

// Carga de PDFs en modo binario durante la inicialización (init context de k6)
const pdfFiles = [
    open('./pdfs/2020-Scrum-Guide-Spanish-Latin-South-American.pdf', 'b'),
    open('./pdfs/Essential-Kanban-Condensed-Spanish.pdf', 'b'),
    open('./pdfs/Filosofia Lean.pdf', 'b'),
    open('./pdfs/scrum_manager_historias_usuario.pdf', 'b'),
];

export default function () {
    // Selección aleatoria de un PDF de la lista
    const randomPdf = pdfFiles[Math.floor(Math.random() * pdfFiles.length)];

    const payload = {
        file: http.file(randomPdf, 'documento.pdf', 'application/pdf'),
    };
    const res = http.post(`${BASE_URL}/upload-pdf`, payload);

    statusTrend.add(res.status);

    check(res, {
        'status 201 o 409': (r) => r.status === 201 || r.status === 409,
    });
}


