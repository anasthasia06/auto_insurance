"""Endpoints de santé de l'API."""

import logging

from fastapi import APIRouter, Depends
from auto_insurance.api.dependencies import get_pipeline

logger = logging.getLogger(__name__)
from auto_insurance.api.schemas.insurance import HealthResponse
from auto_insurance.src.pipeline import PredictionPipeline

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check() -> HealthResponse:
    """
    Vérifie que l'API est opérationnelle.

    Returns:
        Statut et message de confirmation.
    """
    logger.info("GET /health")
    return HealthResponse(status="ok", message="API opérationnelle")


@router.get("/health/models", tags=["Health"])
def health_models(
    pipeline: PredictionPipeline = Depends(get_pipeline),
) -> dict:
    """
    Vérifie que les modèles XGBoost sont bien chargés.

    Returns:
        Informations sur les modèles chargés.
    """
    logger.info("GET /health/models")
    return {
        "status": "ok",
        "models": {
            "frequence": {
                "loaded": pipeline.model.model_frequence is not None,
                "features": len(pipeline.model.model_frequence.feature_names_in_),
                "version": "v1.0"
            },
            "gravite": {
                "loaded": pipeline.model.model_gravite is not None,
                "features": len(pipeline.model.model_gravite.feature_names_in_),
                "version": "v1.0"
            }
        }
    }
