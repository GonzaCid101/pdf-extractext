"""Lectura técnica del archivo subido: chunks en memoria, sin tocar disco."""

import hashlib

from fastapi import UploadFile

from app.services.upload_policy import UploadPolicy

CHUNK_SIZE = 1024 * 1024


async def read_upload(file: UploadFile, policy: UploadPolicy) -> tuple[bytes, str]:
    """Devuelve el contenido del archivo y su checksum SHA-256.

    El checksum se calcula en la misma pasada para no releer el archivo, y el
    tamaño se contrasta contra la política en cada chunk para cortar la
    lectura en cuanto se supera el límite.
    """
    # El tamaño declarado permite rechazar el archivo antes de leer el cuerpo.
    if file.size is not None:
        policy.validate_size(file.size)

    buffer = bytearray()
    hasher = hashlib.sha256()
    total_size = 0
    while chunk := await file.read(CHUNK_SIZE):
        total_size += len(chunk)
        policy.validate_size(total_size)
        hasher.update(chunk)
        buffer.extend(chunk)

    return bytes(buffer), hasher.hexdigest()
