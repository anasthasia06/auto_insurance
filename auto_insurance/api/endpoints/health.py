"""Health endpoints for the API."""

import logging

from fastapi import APIRouter, Depends

from auto_insurance.api.dependencies import get_pipeline
from auto_insurance.api.schemas.insurance import HealthResponse
from auto_insurance.src.pipeline import PredictionPipeline

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check() -> HealthResponse:
    """Return a basic health status."""
    logger.info("GET /health")
    return HealthResponse(status="ok", message="API operationnelle")


@router.get("/health/models", tags=["Health"])
def health_models(
    pipeline: PredictionPipeline = Depends(get_pipeline),
) -> dict:
    """Return model loading details."""
    logger.info("GET /health/models")
    return {
        "status": "ok",
        "models": {
            "frequence": {
                "loaded": pipeline.model.model_frequence is not None,
                "features": len(pipeline.model.model_frequence.feature_names_in_),
                "version": "v1.0",
            },
            "gravite": {
                "loaded": pipeline.model.model_gravite is not None,
                "features": len(pipeline.model.model_gravite.feature_names_in_),
                "version": "v1.0",
            },
        },
    }
