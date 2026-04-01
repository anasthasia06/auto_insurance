"""
Endpoints de prédiction pour l'assurance auto.
/predict/frequency — probabilité de sinistre
/predict/severity  — coût moyen d'un sinistre
/predict/premium   — prime pure (fréquence × gravité)
"""

from fastapi import APIRouter, Depends, HTTPException
import pandas as pd
import numpy as np

from auto_insurance.api.schemas.insurance import (
    FrequenceResponse,
    GraviteResponse,
    InsuranceInput,
    PrimeResponse,
)
from auto_insurance.src.model import InsuranceModel

router = APIRouter(prefix="/predict", tags=["Predictions"])

# --- NOTRE ASTUCE DEVOPS ---
# Au lieu d'importer depuis un fichier cassé, on instancie le modèle directement ici !
_insurance_model = InsuranceModel()

def get_model():
    return _insurance_model
# ---------------------------

EXPECTED_COLS = [
    "type_contrat", "duree_contrat", "anciennete_info", "freq_paiement",
    "utilisation", "code_postal", "age_conducteur1", "sex_conducteur1",
    "anciennete_permis1", "anciennete_vehicule", "cylindre_vehicule",
    "din_vehicule", "essence_vehicule", "marque_vehicule", "modele_vehicule",
    "fin_vente_vehicule", "vitesse_vehicule", "type_vehicule", "prix_vehicule",
    "poids_vehicule", "ratio_poids_puissance", "age_obtention_permis",
    "duree_vie_modele", "log_prix_vehicule"
]


def _get_risk_level(frequence: float) -> str:
    """Retourne le niveau de risque selon la fréquence prédite."""
    if frequence < 0.05:
        return "faible"
    if frequence < 0.10:
        return "modéré"
    if frequence < 0.20:
        return "élevé"
    return "très élevé"


def _prepare_features(data: InsuranceInput) -> pd.DataFrame:
    """Construit le DataFrame avec les 24 features exactes attendues par XGBoost."""
    try:
        d = data.model_dump()
        ratio = d["poids_vehicule"] / (d["din_vehicule"] + 1e-5)
        age_permis = d["age_conducteur1"] - d["anciennete_permis1"]
        duree_vie = d["fin_vente_vehicule"] - d.get("debut_vente_vehicule", d["fin_vente_vehicule"] - 5)
        log_prix = float(np.log1p(d["prix_vehicule"]))

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
        # Notre correction object qui marchait si bien !
        cat_cols = df.select_dtypes(include="object").columns
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
    return FrequenceResponse(
        frequence_predite=round(model.predict_frequence(df), 4)
    )


@router.post("/severity", response_model=GraviteResponse)
def predict_severity(
    data: InsuranceInput,
    model: InsuranceModel = Depends(get_model),
) -> GraviteResponse:
    """Prédit le coût moyen d'un sinistre (gravité)."""
    df = _prepare_features(data)
    return GraviteResponse(
        cout_moyen_predit=round(model.predict_gravite(df), 2)
    )


@router.post("/premium", response_model=PrimeResponse)
def predict_premium(
    data: InsuranceInput,
    model: InsuranceModel = Depends(get_model),
) -> PrimeResponse:
    """Calcule la prime pure = fréquence × gravité."""
    df = _prepare_features(data)
    result = model.predict_prime(df)
    frequence = round(result["frequence_predite"], 4)
    gravite = round(result["cout_moyen_predit"], 2)
    prime = round(result["prime_pure"], 2)
    return PrimeResponse(
        frequence_predite=frequence,
        cout_moyen_predit=gravite,
        prime_pure=prime,
        niveau_risque=_get_risk_level(frequence),
        model_version="v1.0"
    )
    
@router.post("/explain", tags=["Predictions"])
def predict_explain(
    data: InsuranceInput,
    model: InsuranceModel = Depends(get_model),
) -> dict:
    """
    Explique les facteurs qui influencent la prime calculée.
    """
    df = _prepare_features(data)
    result = model.predict_prime(df)
    frequence = round(result["frequence_predite"], 4)
    gravite = round(result["cout_moyen_predit"], 2)
    prime = round(result["prime_pure"], 2)

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

    return {
        "frequence_predite": frequence,
        "cout_moyen_predit": gravite,
        "prime_pure": prime,
        "niveau_risque": _get_risk_level(frequence),
        "facteurs_de_risque": facteurs,
        "model_version": "v1.0"
    }
