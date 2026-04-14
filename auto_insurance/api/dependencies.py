"""FastAPI dependency providers for the application."""

from auto_insurance.api.persistence import (
    PredictionAuditRepository,
    build_audit_repository,
)
from auto_insurance.src.pipeline import PredictionPipeline

<<<<<<< HEAD
_pipeline: PredictionPipeline | None = None
_audit_repository: PredictionAuditRepository | None = None
=======
# OPTIONAL import (safe)
try:
    from auto_insurance.api.persistence import (
        PredictionAuditRepository,
        build_audit_repository,
    )
    AUDIT_AVAILABLE = True
except ImportError:
    PredictionAuditRepository = None
    build_audit_repository = None
    AUDIT_AVAILABLE = False


_pipeline: PredictionPipeline | None = None
_audit_repository = None
>>>>>>> dev


def get_pipeline() -> PredictionPipeline:
    """Return the prediction pipeline singleton."""
    global _pipeline
    if _pipeline is None:
        _pipeline = PredictionPipeline()
    return _pipeline


<<<<<<< HEAD
def get_audit_repository() -> PredictionAuditRepository:
    """Return the audit repository singleton."""
    global _audit_repository
    if _audit_repository is None:
        _audit_repository = build_audit_repository()
    return _audit_repository
=======
def get_audit_repository():
    """Return audit repository if available."""
    global _audit_repository

    if not AUDIT_AVAILABLE:
        return None

    if _audit_repository is None:
        _audit_repository = build_audit_repository()

    return _audit_repository
>>>>>>> dev
