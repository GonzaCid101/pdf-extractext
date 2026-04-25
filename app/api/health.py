"""Endpoint de health check."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def health_check():
    """Verifica estado de la API."""
    return {"message": "PDF Extractext API funcionando"}
