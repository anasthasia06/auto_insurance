"""
Endpoints de prédiction pour l'assurance auto.
/predict/frequency — probabilité de sinistre
/predict/severity  — coût moyen d'un sinistre
/predict/premium   — prime pure (fréquence × gravité)
"""

from fastapi import APIRouter, Depends, HTTPException
import pandas as pd
from auto_insurance.api.dependencies import get_feature_engineer, get_model, get_preprocessor
from auto_insurance.api.schemas.insurance import (
    FrequenceResponse,
    GraviteResponse,
    InsuranceInput,
    PrimeResponse,
)
from auto_insurance.src.features import FeatureEngineer
from auto_insurance.src.model import InsuranceModel
from auto_insurance.src.preprocessing import DataPreprocessor

router = APIRouter(prefix="/predict", tags=["Predictions"])


def _prepare_features(
    data: InsuranceInput,
    preprocessor: DataPreprocessor,
    feature_engineer: FeatureEngineer,
):

    """Pipeline commun : préprocessing + feature engineering."""
    try:

        df = preprocessor.transform(data.model_dump())

        df = feature_engineer.transform(df)

    except Exception as e:

        raise HTTPException(status_code=422, detail=f"Erreur de préprocessing : {e}") from e

    return df

@router.post("/frequency", response_model=FrequenceResponse)
def predict_frequency(
    data: InsuranceInput,
    model: InsuranceModel = Depends(get_model),
    preprocessor: DataPreprocessor = Depends(get_preprocessor),
    feature_engineer: FeatureEngineer = Depends(get_feature_engineer),
) -> FrequenceResponse:
    """
    Prédit la probabilité de sinistre (fréquence).

    Args:
        data: Données brutes du contrat d'assurance.

    Returns:
        Fréquence prédite (entre 0 et 1).
    """
    df = _prepare_features(data, preprocessor, feature_engineer)
    frequence = model.predict_frequence(df)
    return FrequenceResponse(frequence_predite=frequence)


@router.post("/severity", response_model=GraviteResponse)
def predict_severity(
    data: InsuranceInput,
    model: InsuranceModel = Depends(get_model),
    preprocessor: DataPreprocessor = Depends(get_preprocessor),
    feature_engineer: FeatureEngineer = Depends(get_feature_engineer),
) -> GraviteResponse:
    """
    Prédit le coût moyen d'un sinistre (gravité).

    Args:
        data: Données brutes du contrat d'assurance.

    Returns:
        Coût moyen prédit en euros.
    """
    df = _prepare_features(data, preprocessor, feature_engineer)
    gravite = model.predict_gravite(df)
    return GraviteResponse(cout_moyen_predit=gravite)


@router.post("/premium", response_model=PrimeResponse)
def predict_premium(
    data: InsuranceInput,
    model: InsuranceModel = Depends(get_model),
    preprocessor: DataPreprocessor = Depends(get_preprocessor),
    feature_engineer: FeatureEngineer = Depends(get_feature_engineer),
) -> PrimeResponse:
    """
    Calcule la prime pure = fréquence × gravité.

    Args:
        data: Données brutes du contrat d'assurance.

    Returns:
        Fréquence, gravité et prime pure en euros.
    """
    df = _prepare_features(data, preprocessor, feature_engineer)
    result = model.predict_prime(df)
    return PrimeResponse(**result)
