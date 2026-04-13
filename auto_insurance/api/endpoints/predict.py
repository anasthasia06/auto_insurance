"""
Endpoints de prédiction pour l'assurance auto.
/predict/frequency — probabilité de sinistre
/predict/severity  — coût moyen d'un sinistre
/predict/premium   — prime pure (fréquence × gravité)
/predict/explain   — prime + facteurs de risque explicatifs
"""

from fastapi import APIRouter, Depends, HTTPException

from auto_insurance.api.dependencies import get_pipeline
from auto_insurance.api.schemas.insurance import (
    FrequenceResponse,
    GraviteResponse,
    InsuranceInput,
    PrimeResponse,
)
from auto_insurance.src.pipeline import PredictionPipeline

router = APIRouter(prefix="/predict", tags=["Predictions"])


def _get_risk_level(frequence: float) -> str:
    """Retourne le niveau de risque selon la fréquence prédite."""
    if frequence < 0.05:
        return "faible"
    if frequence < 0.10:
        return "modéré"
    if frequence < 0.20:
        return "élevé"
    return "très élevé"


def _get_risk_factors(data: InsuranceInput) -> list[str]:
    """Retourne les facteurs de risque détectés."""
    facteurs = []
    if data.age_conducteur1 < 25:
        facteurs.append("Conducteur jeune — risque plus élevé")
    if data.din_vehicule > 150:
        facteurs.append("Véhicule puissant — risque accru")
    if data.prix_vehicule > 30000:
        facteurs.append("Véhicule haut de gamme — coût de réparation élevé")
    if data.anciennete_permis1 < 3:
        facteurs.append("Permis récent — manque d'expérience")
    if data.anciennete_vehicule > 10:
        facteurs.append("Véhicule ancien — risque de panne")
    if not facteurs:
        facteurs.append("Profil standard — pas de facteur de risque majeur")
    return facteurs


@router.post("/frequency", response_model=FrequenceResponse)
def predict_frequency(
    data: InsuranceInput,
    pipeline: PredictionPipeline = Depends(get_pipeline),
) -> FrequenceResponse:
    """Prédit la probabilité de sinistre (fréquence)."""
    try:
        frequence = pipeline.predict_frequence(data.model_dump())
        return FrequenceResponse(frequence_predite=frequence)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction : {e}") from e


@router.post("/severity", response_model=GraviteResponse)
def predict_severity(
    data: InsuranceInput,
    pipeline: PredictionPipeline = Depends(get_pipeline),
) -> GraviteResponse:
    """Prédit le coût moyen d'un sinistre (gravité)."""
    try:
        gravite = pipeline.predict_gravite(data.model_dump())
        return GraviteResponse(cout_moyen_predit=gravite)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction : {e}") from e


@router.post("/premium", response_model=PrimeResponse)
def predict_premium(
    data: InsuranceInput,
    pipeline: PredictionPipeline = Depends(get_pipeline),
) -> PrimeResponse:
    """Calcule la prime pure = fréquence × gravité."""
    try:
        result = pipeline.predict_prime(data.model_dump())
        return PrimeResponse(
            frequence_predite=result["frequence_predite"],
            cout_moyen_predit=result["cout_moyen_predit"],
            prime_pure=result["prime_pure"],
            niveau_risque=_get_risk_level(result["frequence_predite"]),
            model_version="v1.0"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction : {e}") from e


@router.post("/explain", tags=["Predictions"])
def predict_explain(
    data: InsuranceInput,
    pipeline: PredictionPipeline = Depends(get_pipeline),
) -> dict:
    """Explique les facteurs qui influencent la prime calculée."""
    try:
        result = pipeline.predict_prime(data.model_dump())
        return {
            "frequence_predite": result["frequence_predite"],
            "cout_moyen_predit": result["cout_moyen_predit"],
            "prime_pure": result["prime_pure"],
            "niveau_risque": _get_risk_level(result["frequence_predite"]),
            "facteurs_de_risque": _get_risk_factors(data),
            "model_version": "v1.0"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction : {e}") from e
