"""Endpoint de santé de l'API."""

from fastapi import APIRouter
from auto_insurance.api.schemas.insurance import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check() -> HealthResponse:
    """
    Vérifie que l'API est opérationnelle.

    Returns:
        Statut et message de confirmation.
    """
    return HealthResponse(status="ok", message="API opérationnelle")
