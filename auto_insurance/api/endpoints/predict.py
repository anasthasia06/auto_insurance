<<<<<<< HEAD
"""Prediction endpoints for the auto insurance API."""
=======
"""
Prediction endpoints for the AutoAssur motor insurance pricing API.

/predict/frequency — claim probability (frequency model)
/predict/severity  — average claim cost (severity model)
/predict/premium   — pure premium = frequency x severity
/predict/explain   — pure premium + top risk factors (SHAP)

Error handling strategy:
- ValueError   -> 422: invalid business data (e.g. feature out of expected range)
- KeyError     -> 400: expected feature missing from the pipeline
- RuntimeError -> 503: model unavailable (e.g. model file not loaded)
- Exception    -> 500: unexpected system error (full traceback logged)
"""
>>>>>>> dev

import logging
import time

<<<<<<< HEAD
=======
import shap
>>>>>>> dev
from fastapi import APIRouter, Depends, HTTPException

from auto_insurance.api.dependencies import get_audit_repository, get_pipeline
from auto_insurance.api.persistence import PredictionAuditRepository
from auto_insurance.api.schemas.insurance import (
<<<<<<< HEAD
=======
    MODEL_VERSION,
    ExplainResponse,
>>>>>>> dev
    FrequenceResponse,
    GraviteResponse,
    InsuranceInput,
    PrimeResponse,
)
from auto_insurance.src.pipeline import PredictionPipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/predict", tags=["Predictions"])
logger = logging.getLogger(__name__)


<<<<<<< HEAD
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
=======
# ── Helpers ──────────────────────────────────────────────────────────────────

def _get_risk_level(frequency: float) -> str:
    """
    Map a predicted claim frequency to a human-readable risk level.

    Thresholds calibrated on the training data distribution:
    - low      : < 5%  annual claim probability
    - moderate : 5% – 10%
    - high     : 10% – 20%
    - very high: > 20%

    Args:
        frequency: Predicted claim probability, clamped in [0, 1].

    Returns:
        Risk level string: "faible" | "modéré" | "élevé" | "très élevé"
    """
    if frequency < 0.05:
        return "faible"
    if frequency < 0.10:
        return "modéré"
    if frequency < 0.20:
        return "élevé"
    return "très élevé"


def _get_risk_factors(
    data: InsuranceInput,
    pipeline: PredictionPipeline,
) -> list[str]:
    """
    Compute the top 3 risk factors using SHAP TreeExplainer.

    SHAP (SHapley Additive exPlanations) assigns each feature its marginal
    contribution to the prediction. A positive SHAP value means the feature
    increases the predicted risk; a negative value means it decreases it.

    The frequency model is used for explanation, as frequency is the primary
    driver of risk classification.

    Args:
        data: Validated input data from the Pydantic schema.
        pipeline: Loaded prediction pipeline (singleton).

    Returns:
        List of 3 strings describing the most influential features.

    Raises:
        RuntimeError: If the SHAP computation fails.
    """
    df = pipeline._build_features(data.model_dump())

    # SHAP TreeExplainer does not support pandas "category" dtype.
    # Convert categorical columns to integer codes before computing SHAP values.
    df_shap = df.copy()
    for col in df_shap.select_dtypes(include="category").columns:
        df_shap[col] = df_shap[col].cat.codes

    explainer = shap.TreeExplainer(pipeline.model.model_frequence)
    shap_values = explainer.shap_values(df_shap)

    feature_names = df_shap.columns.tolist()
    shap_importance = dict(zip(feature_names, shap_values[0]))

    top_features = sorted(
        shap_importance.items(),
        key=lambda x: abs(x[1]),
        reverse=True,
    )[:3]

    return [
        f"{feature} {'augmente' if value > 0 else 'diminue'} le risque"
        for feature, value in top_features
    ]


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post(
    "/frequency",
    response_model=FrequenceResponse,
    summary="Claim probability",
    description=(
        "Predicts the probability that a claim will occur during the contract period. "
        "Output is clamped between 0 (no risk) and 1 (certain claim). "
        "Powered by an XGBoost model trained on historical claims data."
    ),
)
>>>>>>> dev
def predict_frequency(
    data: InsuranceInput,
    pipeline: PredictionPipeline = Depends(get_pipeline),
    audit_repository: PredictionAuditRepository = Depends(get_audit_repository),
) -> FrequenceResponse:
<<<<<<< HEAD
    """Predict claim frequency."""
    try:
        frequence = pipeline.predict_frequence(data.model_dump())
        response = FrequenceResponse(frequence_predite=frequence)
        audit_repository.save_prediction(
            endpoint="/predict/frequency",
            request_payload=data.model_dump(),
            response_payload=response.model_dump(),
        )
        logger.info("Frequency prediction served for postal code %s", data.code_postal)
        return response
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Erreur de prediction : {exc}"
        ) from exc
=======
    """Predict claim frequency (probability) for a given insurance contract."""
    start = time.perf_counter()
    try:
        frequency = pipeline.predict_frequence(data.model_dump())

        logger.info(
            "Frequency prediction successful",
            extra={
                "endpoint": "/predict/frequency",
                "latency_ms": round((time.perf_counter() - start) * 1000, 2),
                "vehicle_brand": data.marque_vehicule,
                "model_version": MODEL_VERSION,
            },
        )
        return FrequenceResponse(frequence_predite=frequency)

    except ValueError as e:
        # Business data is invalid after Pydantic validation
        # e.g. a computed feature falls outside the range expected by the model
        logger.warning(
            "Invalid data for frequency prediction",
            extra={
                "endpoint": "/predict/frequency",
                "error_type": "ValueError",
                "error_detail": str(e),
            },
        )
        raise HTTPException(
            status_code=422,
            detail=f"Invalid input data: {e}",
        ) from e

    except KeyError as e:
        # A feature expected by the model is missing from the DataFrame
        logger.error(
            "Missing feature in frequency pipeline",
            extra={
                "endpoint": "/predict/frequency",
                "error_type": "KeyError",
                "error_detail": str(e),
            },
        )
        raise HTTPException(
            status_code=400,
            detail=(
                f"Missing feature in pipeline: {e}. "
                "Ensure all required input fields are provided."
            ),
        ) from e

    except RuntimeError as e:
        # Internal model error (model not loaded, XGBoost incompatibility)
        logger.error(
            "Frequency model internal error",
            extra={
                "endpoint": "/predict/frequency",
                "error_type": "RuntimeError",
                "error_detail": str(e),
            },
        )
        raise HTTPException(
            status_code=503,
            detail=(
                "The frequency model is temporarily unavailable. "
                "Please verify that model files are correctly loaded."
            ),
        ) from e

    except Exception as e:
        # Unexpected system error — log full traceback
        logger.exception(
            "Unexpected system error on /predict/frequency",
            extra={
                "endpoint": "/predict/frequency",
                "error_type": type(e).__name__,
            },
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Check server logs for details.",
        ) from e
>>>>>>> dev


@router.post(
    "/severity",
    response_model=GraviteResponse,
    summary="Average claim cost",
    description=(
        "Predicts the average cost of a claim if one occurs. "
        "Output is expressed in euros (always positive). "
        "Powered by an XGBoost severity model trained on historical claims data."
    ),
)
def predict_severity(
    data: InsuranceInput,
    pipeline: PredictionPipeline = Depends(get_pipeline),
    audit_repository: PredictionAuditRepository = Depends(get_audit_repository),
) -> GraviteResponse:
<<<<<<< HEAD
    """Predict claim severity."""
    try:
        gravite = pipeline.predict_gravite(data.model_dump())
        response = GraviteResponse(cout_moyen_predit=gravite)
        audit_repository.save_prediction(
            endpoint="/predict/severity",
            request_payload=data.model_dump(),
            response_payload=response.model_dump(),
        )
        logger.info("Severity prediction served for vehicle %s", data.modele_vehicule)
        return response
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Erreur de prediction : {exc}"
        ) from exc
=======
    """Predict claim severity (average cost) for a given insurance contract."""
    start = time.perf_counter()
    try:
        severity = pipeline.predict_gravite(data.model_dump())

        logger.info(
            "Severity prediction successful",
            extra={
                "endpoint": "/predict/severity",
                "latency_ms": round((time.perf_counter() - start) * 1000, 2),
                "vehicle_brand": data.marque_vehicule,
                "model_version": MODEL_VERSION,
            },
        )
        return GraviteResponse(cout_moyen_predit=severity)

    except ValueError as e:
        logger.warning(
            "Invalid data for severity prediction",
            extra={
                "endpoint": "/predict/severity",
                "error_type": "ValueError",
                "error_detail": str(e),
            },
        )
        raise HTTPException(
            status_code=422,
            detail=f"Invalid input data: {e}",
        ) from e

    except KeyError as e:
        logger.error(
            "Missing feature in severity pipeline",
            extra={
                "endpoint": "/predict/severity",
                "error_type": "KeyError",
                "error_detail": str(e),
            },
        )
        raise HTTPException(
            status_code=400,
            detail=f"Missing feature in pipeline: {e}.",
        ) from e

    except RuntimeError as e:
        logger.error(
            "Severity model internal error",
            extra={
                "endpoint": "/predict/severity",
                "error_type": "RuntimeError",
                "error_detail": str(e),
            },
        )
        raise HTTPException(
            status_code=503,
            detail="The severity model is temporarily unavailable.",
        ) from e

    except Exception as e:
        logger.exception(
            "Unexpected system error on /predict/severity",
            extra={
                "endpoint": "/predict/severity",
                "error_type": type(e).__name__,
            },
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Check server logs for details.",
        ) from e
>>>>>>> dev


@router.post(
    "/premium",
    response_model=PrimeResponse,
    summary="Full pure premium",
    description=(
        "Computes the **pure premium** using the standard actuarial formula:\n\n"
        "`Pure Premium = Frequency × Severity`\n\n"
        "Also returns a risk level (low / moderate / high / very high) "
        "derived from the predicted claim frequency."
    ),
)
def predict_premium(
    data: InsuranceInput,
    pipeline: PredictionPipeline = Depends(get_pipeline),
    audit_repository: PredictionAuditRepository = Depends(get_audit_repository),
) -> PrimeResponse:
<<<<<<< HEAD
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
        logger.info(
            "Premium prediction served for %s %s with risk level %s",
            data.marque_vehicule,
            data.modele_vehicule,
            response.niveau_risque,
        )
        return response
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Erreur de prediction : {exc}"
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
        logger.info("Explain prediction served for contract type %s", data.type_contrat)
        return response
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"Erreur de prediction : {exc}"
        ) from exc
=======
    """Compute the pure premium = frequency x severity."""
    start = time.perf_counter()
    try:
        result = pipeline.predict_prime(data.model_dump())
        risk_level = _get_risk_level(result["frequence_predite"])

        logger.info(
            "Premium prediction successful",
            extra={
                "endpoint": "/predict/premium",
                "latency_ms": round((time.perf_counter() - start) * 1000, 2),
                "vehicle_brand": data.marque_vehicule,
                "model_version": MODEL_VERSION,
            },
        )
        return PrimeResponse(
            frequence_predite=result["frequence_predite"],
            cout_moyen_predit=result["cout_moyen_predit"],
            prime_pure=result["prime_pure"],
            niveau_risque=risk_level,
            model_version=MODEL_VERSION,
        )

    except ValueError as e:
        logger.warning(
            "Invalid data for premium computation",
            extra={
                "endpoint": "/predict/premium",
                "error_type": "ValueError",
                "error_detail": str(e),
            },
        )
        raise HTTPException(
            status_code=422,
            detail=f"Invalid input data: {e}",
        ) from e

    except KeyError as e:
        logger.error(
            "Missing feature in premium pipeline",
            extra={
                "endpoint": "/predict/premium",
                "error_type": "KeyError",
                "error_detail": str(e),
            },
        )
        raise HTTPException(
            status_code=400,
            detail=f"Missing feature in pipeline: {e}.",
        ) from e

    except RuntimeError as e:
        logger.error(
            "Model internal error during premium computation",
            extra={
                "endpoint": "/predict/premium",
                "error_type": "RuntimeError",
                "error_detail": str(e),
            },
        )
        raise HTTPException(
            status_code=503,
            detail="Models are temporarily unavailable.",
        ) from e

    except Exception as e:
        logger.exception(
            "Unexpected system error on /predict/premium",
            extra={
                "endpoint": "/predict/premium",
                "error_type": type(e).__name__,
            },
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Check server logs for details.",
        ) from e


@router.post(
    "/explain",
    response_model=ExplainResponse,
    summary="Pure premium + risk factors (SHAP)",
    description=(
        "Computes the pure premium and returns the **top 3 risk factors** "
        "driving the prediction, computed via SHAP TreeExplainer.\n\n"
        "SHAP (SHapley Additive exPlanations) assigns each feature its marginal "
        "contribution to the prediction, providing local explainability. "
        "This endpoint addresses the GDPR Article 22 requirement for "
        "explainability in automated decision-making."
    ),
)
def predict_explain(
    data: InsuranceInput,
    pipeline: PredictionPipeline = Depends(get_pipeline),
) -> ExplainResponse:
    """Compute the pure premium and explain risk factors via SHAP."""
    start = time.perf_counter()
    try:
        result = pipeline.predict_prime(data.model_dump())
        risk_factors = _get_risk_factors(data, pipeline)
        risk_level = _get_risk_level(result["frequence_predite"])

        logger.info(
            "SHAP explanation computed successfully",
            extra={
                "endpoint": "/predict/explain",
                "latency_ms": round((time.perf_counter() - start) * 1000, 2),
                "vehicle_brand": data.marque_vehicule,
                "model_version": MODEL_VERSION,
            },
        )
        return ExplainResponse(
            frequence_predite=result["frequence_predite"],
            cout_moyen_predit=result["cout_moyen_predit"],
            prime_pure=result["prime_pure"],
            niveau_risque=risk_level,
            facteurs_de_risque=risk_factors,
            model_version=MODEL_VERSION,
        )

    except ValueError as e:
        logger.warning(
            "Invalid data for SHAP explanation",
            extra={
                "endpoint": "/predict/explain",
                "error_type": "ValueError",
                "error_detail": str(e),
            },
        )
        raise HTTPException(
            status_code=422,
            detail=f"Invalid input data: {e}",
        ) from e

    except KeyError as e:
        logger.error(
            "Missing feature in explain pipeline",
            extra={
                "endpoint": "/predict/explain",
                "error_type": "KeyError",
                "error_detail": str(e),
            },
        )
        raise HTTPException(
            status_code=400,
            detail=f"Missing feature in pipeline: {e}.",
        ) from e

    except RuntimeError as e:
        logger.error(
            "SHAP or model error on /predict/explain",
            extra={
                "endpoint": "/predict/explain",
                "error_type": "RuntimeError",
                "error_detail": str(e),
            },
        )
        raise HTTPException(
            status_code=503,
            detail="SHAP computation is temporarily unavailable.",
        ) from e

    except Exception as e:
        logger.exception(
            "Unexpected system error on /predict/explain",
            extra={
                "endpoint": "/predict/explain",
                "error_type": type(e).__name__,
            },
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Check server logs for details.",
        ) from e
>>>>>>> dev
