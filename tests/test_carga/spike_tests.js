import http from 'k6/http';
import { Trend } from 'k6/metrics';
import { check } from 'k6';

const statusTrend = new Trend('status_codes');

export const options = {
    insecureSkipTLSVerify: true,

    stages: [
        { duration: '10s', target: 100 },
        { duration: '20s', target: 100 },
        { duration: '10s', target: 0 },
    ],
};

const BASE_URL = 'https://127.0.0.1';

const pdfFiles = [
    open('./pdfs/2020-Scrum-Guide-Spanish-Latin-South-American.pdf', 'b'),
    open('./pdfs/Essential-Kanban-Condensed-Spanish.pdf', 'b'),
    open('./pdfs/Filosofia Lean.pdf', 'b'),
    open('./pdfs/scrum_manager_historias_usuario.pdf', 'b'),
];

export default function () {
    const randomPdf =
        pdfFiles[Math.floor(Math.random() * pdfFiles.length)];

    const formData = {
        file: http.file(
            randomPdf,
            'archivo.pdf',
            'application/pdf'
        ),
    };

    const res = http.post(
        `${BASE_URL}/upload-pdf`,
        formData,
        {
            headers: {
                Host: 'pdf-extractext.universidad.localhost',
            },
        }
    );

    statusTrend.add(res.status);

    check(res, {
        'status 201 or 409': (r) =>
            r.status === 201 || r.status === 409,
    });
}