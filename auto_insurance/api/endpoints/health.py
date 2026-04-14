"""Health endpoints for the API."""

import logging
from fastapi import APIRouter, Depends

<<<<<<< HEAD
from auto_insurance.api.dependencies import get_audit_repository, get_pipeline
from auto_insurance.api.persistence import PredictionAuditRepository
from auto_insurance.api.schemas.insurance import HealthResponse
from auto_insurance.src.pipeline import PredictionPipeline

=======
from auto_insurance.api.dependencies import get_pipeline
from auto_insurance.api.schemas.insurance import HealthResponse
from auto_insurance.src.pipeline import PredictionPipeline

# OPTIONAL import (safe)
try:
    from auto_insurance.api.persistence import PredictionAuditRepository
    from auto_insurance.api.dependencies import get_audit_repository
    AUDIT_AVAILABLE = True
except ImportError:
    PredictionAuditRepository = None
    get_audit_repository = None
    AUDIT_AVAILABLE = False

>>>>>>> dev
logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check() -> HealthResponse:
<<<<<<< HEAD
    """Return a basic health status."""
=======
    """Basic API health."""
>>>>>>> dev
    logger.info("GET /health")
    return HealthResponse(status="ok", message="API operationnelle")


@router.get("/health/models", tags=["Health"])
def health_models(
    pipeline: PredictionPipeline = Depends(get_pipeline),
) -> dict:
<<<<<<< HEAD
    """Return model loading details."""
=======
    """Check if models are loaded."""
>>>>>>> dev
    logger.info("GET /health/models")

    return {
        "status": "ok",
        "models": {
            "frequence": {
                "loaded": pipeline.model.model_frequence is not None,
<<<<<<< HEAD
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
    logger.info("GET /health/audit")
    return {
        "status": "ok",
        "audit": audit_repository.get_status(),
=======
            },
            "gravite": {
                "loaded": pipeline.model.model_gravite is not None,
            },
        },
>>>>>>> dev
    }


@router.get("/health/audit", tags=["Health"])
def health_audit():
    """Audit status (optional)."""
    logger.info("GET /health/audit")

    if not AUDIT_AVAILABLE:
        return {
            "status": "disabled",
            "message": "Audit repository not configured",
        }

    try:
        audit_repository = get_audit_repository()
        return {
            "status": "ok",
            "audit": audit_repository.get_status(),
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }