"""Endpoints de santé de l'API."""

from fastapi import APIRouter, Depends
from auto_insurance.api.dependencies import get_model
from auto_insurance.api.schemas.insurance import HealthResponse
from auto_insurance.src.model import InsuranceModel

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check() -> HealthResponse:
    """
    Vérifie que l'API est opérationnelle.

    Returns:
        Statut et message de confirmation.
    """
    return HealthResponse(status="ok", message="API opérationnelle")


@router.get("/health/models", tags=["Health"])
def health_models(model: InsuranceModel = Depends(get_model)) -> dict:
    """
    Vérifie que les modèles XGBoost sont bien chargés.

    Returns:
        Informations sur les modèles chargés.
    """
    return {
        "status": "ok",
        "models": {
            "frequence": {
                "loaded": model.model_frequence is not None,
                "features": len(model.model_frequence.feature_names_in_),
                "version": "v1.0"
            },
            "gravite": {
                "loaded": model.model_gravite is not None,
                "features": len(model.model_gravite.feature_names_in_),
                "version": "v1.0"
            }
        }
    }