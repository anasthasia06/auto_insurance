"""Prediction endpoints for the auto insurance API."""

from fastapi import APIRouter, Depends, HTTPException

from auto_insurance.api.dependencies import get_audit_repository, get_pipeline
from auto_insurance.api.persistence import PredictionAuditRepository
from auto_insurance.api.schemas.insurance import (
    FrequenceResponse,
    GraviteResponse,
    InsuranceInput,
    PrimeResponse,
)
from auto_insurance.src.pipeline import PredictionPipeline

router = APIRouter(prefix="/predict", tags=["Predictions"])


def _get_risk_level(frequence: float) -> str:
    """Return a risk level label based on predicted frequency."""
    if frequence < 0.05:
        return "faible"
    if frequence < 0.10:
        return "modere"
    if frequence < 0.20:
        return "eleve"
    return "tres eleve"


def _get_risk_factors(data: InsuranceInput) -> list[str]:
    """Return a list of simple risk factors."""
    facteurs = []
    if data.age_conducteur1 < 25:
        facteurs.append("Conducteur jeune - risque plus eleve")
    if data.din_vehicule > 150:
        facteurs.append("Vehicule puissant - risque accru")
    if data.prix_vehicule > 30000:
        facteurs.append("Vehicule haut de gamme - cout de reparation eleve")
    if data.anciennete_permis1 < 3:
        facteurs.append("Permis recent - manque d'experience")
    if data.anciennete_vehicule > 10:
        facteurs.append("Vehicule ancien - risque de panne")
    if not facteurs:
        facteurs.append("Profil standard - pas de facteur de risque majeur")
    return facteurs


@router.post("/frequency", response_model=FrequenceResponse)
def predict_frequency(
    data: InsuranceInput,
    pipeline: PredictionPipeline = Depends(get_pipeline),
    audit_repository: PredictionAuditRepository = Depends(get_audit_repository),
) -> FrequenceResponse:
    """Predict claim frequency."""
    try:
        frequence = pipeline.predict_frequence(data.model_dump())
        response = FrequenceResponse(frequence_predite=frequence)
        audit_repository.save_prediction(
            endpoint="/predict/frequency",
            request_payload=data.model_dump(),
            response_payload=response.model_dump(),
        )
        return response
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur de prediction : {exc}",
        ) from exc


@router.post("/severity", response_model=GraviteResponse)
def predict_severity(
    data: InsuranceInput,
    pipeline: PredictionPipeline = Depends(get_pipeline),
    audit_repository: PredictionAuditRepository = Depends(get_audit_repository),
) -> GraviteResponse:
    """Predict claim severity."""
    try:
        gravite = pipeline.predict_gravite(data.model_dump())
        response = GraviteResponse(cout_moyen_predit=gravite)
        audit_repository.save_prediction(
            endpoint="/predict/severity",
            request_payload=data.model_dump(),
            response_payload=response.model_dump(),
        )
        return response
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur de prediction : {exc}",
        ) from exc


@router.post("/premium", response_model=PrimeResponse)
def predict_premium(
    data: InsuranceInput,
    pipeline: PredictionPipeline = Depends(get_pipeline),
    audit_repository: PredictionAuditRepository = Depends(get_audit_repository),
) -> PrimeResponse:
    """Compute the pure premium as frequency times severity."""
    try:
        result = pipeline.predict_prime(data.model_dump())
        response = PrimeResponse(
            frequence_predite=result["frequence_predite"],
            cout_moyen_predit=result["cout_moyen_predit"],
            prime_pure=result["prime_pure"],
            niveau_risque=_get_risk_level(result["frequence_predite"]),
            model_version="v1.0",
        )
        audit_repository.save_prediction(
            endpoint="/predict/premium",
            request_payload=data.model_dump(),
            response_payload=response.model_dump(),
            niveau_risque=response.niveau_risque,
        )
        return response
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur de prediction : {exc}",
        ) from exc


@router.post("/explain", tags=["Predictions"])
def predict_explain(
    data: InsuranceInput,
    pipeline: PredictionPipeline = Depends(get_pipeline),
    audit_repository: PredictionAuditRepository = Depends(get_audit_repository),
) -> dict:
    """Explain the premium result with simple risk factors."""
    try:
        result = pipeline.predict_prime(data.model_dump())
        response = {
            "frequence_predite": result["frequence_predite"],
            "cout_moyen_predit": result["cout_moyen_predit"],
            "prime_pure": result["prime_pure"],
            "niveau_risque": _get_risk_level(result["frequence_predite"]),
            "facteurs_de_risque": _get_risk_factors(data),
            "model_version": "v1.0",
        }
        audit_repository.save_prediction(
            endpoint="/predict/explain",
            request_payload=data.model_dump(),
            response_payload=response,
            niveau_risque=response["niveau_risque"],
        )
        return response
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur de prediction : {exc}",
        ) from exc
