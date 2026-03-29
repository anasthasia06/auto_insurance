"""
Endpoints de prédiction pour l'assurance auto.
/predict/frequency — probabilité de sinistre
/predict/severity  — coût moyen d'un sinistre
/predict/premium   — prime pure (fréquence × gravité)
"""

from fastapi import APIRouter, Depends, HTTPException
import pandas as pd

from auto_insurance.api.dependencies import get_model
from auto_insurance.api.schemas.insurance import (
    FrequenceResponse,
    GraviteResponse,
    InsuranceInput,
    PrimeResponse,
)
from auto_insurance.src.model import InsuranceModel

router = APIRouter(prefix="/predict", tags=["Predictions"])

EXPECTED_COLS = [
    "type_contrat", "duree_contrat", "anciennete_info", "freq_paiement",
    "utilisation", "code_postal", "age_conducteur1", "sex_conducteur1",
    "anciennete_permis1", "anciennete_vehicule", "cylindre_vehicule",
    "din_vehicule", "essence_vehicule", "marque_vehicule", "modele_vehicule",
    "fin_vente_vehicule", "vitesse_vehicule", "type_vehicule", "prix_vehicule",
    "poids_vehicule", "ratio_poids_puissance", "age_obtention_permis",
    "duree_vie_modele", "log_prix_vehicule"
]


def _prepare_features(data: InsuranceInput) -> pd.DataFrame:
    """Construit le DataFrame avec les features exactes attendues par XGBoost."""
    try:
        d = data.model_dump()
        # Features calculées manuellement
        ratio = d["poids_vehicule"] / (d["din_vehicule"] + 1e-5)
        age_permis = d["age_conducteur1"] - d["anciennete_permis1"]
        duree_vie = d["fin_vente_vehicule"] - d.get("debut_vente_vehicule", d["fin_vente_vehicule"] - 5)
        log_prix = pd.Series([d["prix_vehicule"]]).apply(lambda x: __import__("numpy").log1p(x))[0]

        row = {
            "type_contrat": d["type_contrat"],
            "duree_contrat": d["duree_contrat"],
            "anciennete_info": d["anciennete_info"],
            "freq_paiement": d["freq_paiement"],
            "utilisation": d["utilisation"],
            "code_postal": d["code_postal"],
            "age_conducteur1": d["age_conducteur1"],
            "sex_conducteur1": d["sex_conducteur1"],
            "anciennete_permis1": d["anciennete_permis1"],
            "anciennete_vehicule": d["anciennete_vehicule"],
            "cylindre_vehicule": d["cylindre_vehicule"],
            "din_vehicule": d["din_vehicule"],
            "essence_vehicule": d["essence_vehicule"],
            "marque_vehicule": d["marque_vehicule"],
            "modele_vehicule": d["modele_vehicule"],
            "fin_vente_vehicule": d["fin_vente_vehicule"],
            "vitesse_vehicule": d["vitesse_vehicule"],
            "type_vehicule": d["type_vehicule"],
            "prix_vehicule": d["prix_vehicule"],
            "poids_vehicule": d["poids_vehicule"],
            "ratio_poids_puissance": ratio,
            "age_obtention_permis": age_permis,
            "duree_vie_modele": duree_vie,
            "log_prix_vehicule": log_prix,
        }
        df = pd.DataFrame([row])
        cat_cols = df.select_dtypes(include="str").columns
        df[cat_cols] = df[cat_cols].astype("category")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Erreur : {e}") from e
    return df


@router.post("/frequency", response_model=FrequenceResponse)
def predict_frequency(
    data: InsuranceInput,
    model: InsuranceModel = Depends(get_model),
) -> FrequenceResponse:
    """Prédit la probabilité de sinistre (fréquence)."""
    df = _prepare_features(data)
    return FrequenceResponse(frequence_predite=model.predict_frequence(df))


@router.post("/severity", response_model=GraviteResponse)
def predict_severity(
    data: InsuranceInput,
    model: InsuranceModel = Depends(get_model),
) -> GraviteResponse:
    """Prédit le coût moyen d'un sinistre (gravité)."""
    df = _prepare_features(data)
    return GraviteResponse(cout_moyen_predit=model.predict_gravite(df))


@router.post("/premium", response_model=PrimeResponse)
def predict_premium(
    data: InsuranceInput,
    model: InsuranceModel = Depends(get_model),
) -> PrimeResponse:
    """Calcule la prime pure = fréquence × gravité."""
    df = _prepare_features(data)
    return PrimeResponse(**model.predict_prime(df))