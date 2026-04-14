"""
Endpoints de prédiction pour l'assurance auto.
/predict/frequency — probabilité de sinistre
/predict/severity  — coût moyen d'un sinistre
/predict/premium   — prime pure (fréquence × gravité)
/predict/explain   — prime + facteurs de risque explicatifs
"""

import logging

from fastapi import APIRouter, Depends

from auto_insurance.api.dependencies import get_audit_repository, get_pipeline
from auto_insurance.api.schemas.insurance import HealthResponse
from auto_insurance.src.pipeline import PredictionPipeline

logger = logging.getLogger(__name__)
router = APIRouter()

import shap

from fastapi import APIRouter, Depends, HTTPException

from auto_insurance.api.dependencies import get_pipeline
from auto_insurance.api.schemas.insurance import (
    ExplainResponse,
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


def _get_risk_factors(data: InsuranceInput, pipeline: PredictionPipeline) -> list[str]:
    """Retourne les facteurs de risque via SHAP values."""
    df = pipeline._build_features(data.model_dump())
    
    # Convertir les colonnes category en codes numériques pour SHAP
    df_shap = df.copy()
    for col in df_shap.select_dtypes(include="category").columns:
        df_shap[col] = df_shap[col].cat.codes

    explainer = shap.TreeExplainer(pipeline.model.model_frequence)
    shap_values = explainer.shap_values(df_shap)

    feature_names = df_shap.columns.tolist()
    shap_importance = dict(zip(feature_names, shap_values[0]))

    top_features = sorted(shap_importance.items(), key=lambda x: abs(x[1]), reverse=True)[:3]

    facteurs = []
    for feature, value in top_features:
        direction = "augmente" if value > 0 else "diminue"
        facteurs.append(f"{feature} {direction} le risque")

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


@router.post("/explain", response_model=ExplainResponse)
def predict_explain(
    data: InsuranceInput,
    pipeline: PredictionPipeline = Depends(get_pipeline),
) -> ExplainResponse:
    """Explique les facteurs qui influencent la prime calculée."""
    try:
        result = pipeline.predict_prime(data.model_dump())
        return ExplainResponse(
            frequence_predite=result["frequence_predite"],
            cout_moyen_predit=result["cout_moyen_predit"],
            prime_pure=result["prime_pure"],
            niveau_risque=_get_risk_level(result["frequence_predite"]),
            facteurs_de_risque=_get_risk_factors(data, pipeline),
            model_version="v1.0",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction : {e}") from e
