"""Health endpoints for the API."""

from fastapi import APIRouter, Depends

from auto_insurance.api.dependencies import get_audit_repository, get_pipeline
from auto_insurance.api.persistence import PredictionAuditRepository
from auto_insurance.api.schemas.insurance import HealthResponse
from auto_insurance.src.pipeline import PredictionPipeline

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check() -> HealthResponse:
    """Return a basic health status."""
    return HealthResponse(status="ok", message="API operationnelle")


@router.get("/health/models", tags=["Health"])
def health_models(
    pipeline: PredictionPipeline = Depends(get_pipeline),
) -> dict:
    """Return model loading details."""
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


@router.get("/health/audit", tags=["Health"])
def health_audit(
    audit_repository: PredictionAuditRepository = Depends(get_audit_repository),
) -> dict:
    """Expose optional audit database status."""
    return {
        "status": "ok",
        "audit": audit_repository.get_status(),
    }
