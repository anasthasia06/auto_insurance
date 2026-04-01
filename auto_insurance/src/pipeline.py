"""
Pipeline d'inférence pour l'assurance auto.
Orchestre le feature engineering et la prédiction.
"""

import logging
from pathlib import Path

import numpy as np
import pandas as pd

from auto_insurance.src.model import InsuranceModel

logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).parent.parent / "models"

EXPECTED_COLS = [
    "type_contrat", "duree_contrat", "anciennete_info", "freq_paiement",
    "utilisation", "code_postal", "age_conducteur1", "sex_conducteur1",
    "anciennete_permis1", "anciennete_vehicule", "cylindre_vehicule",
    "din_vehicule", "essence_vehicule", "marque_vehicule", "modele_vehicule",
    "fin_vente_vehicule", "vitesse_vehicule", "type_vehicule", "prix_vehicule",
    "poids_vehicule", "ratio_poids_puissance", "age_obtention_permis",
    "duree_vie_modele", "log_prix_vehicule"
]


class PredictionPipeline:
    """
    Pipeline complet d'inférence : input brut → prime pure.

    Attributes:
        model: Modèles XGBoost fréquence et gravité.
    """

    def __init__(self) -> None:
        self.model = InsuranceModel()
        self._load()

    def _load(self) -> None:
        """Charge les modèles au démarrage."""
        self.model.load_models(
            str(MODELS_DIR / "model_frequence.json"),
            str(MODELS_DIR / "model_gravite.json"),
        )
        logger.info("Pipeline chargé avec succès.")

    def _build_features(self, input_data: dict) -> pd.DataFrame:
        """
        Construit le DataFrame avec les 24 features exactes attendues par XGBoost.

        Args:
            input_data: Dictionnaire des données brutes.

        Returns:
            DataFrame aligné et prêt pour la prédiction.
        """
        d = input_data

        # Features calculées
        ratio = d["poids_vehicule"] / (d["din_vehicule"] + 1e-5)
        age_permis = max(0.0, d["age_conducteur1"] - d["anciennete_permis1"])
        duree_vie = d["fin_vente_vehicule"] - d.get(
            "debut_vente_vehicule", d["fin_vente_vehicule"] - 5
        )
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

        # Alignement strict des colonnes attendues
        for col in EXPECTED_COLS:
            if col not in df.columns:
                df[col] = 0
        df = df[EXPECTED_COLS]

        # Conversion pour XGBoost
        cat_cols = df.select_dtypes(include="str").columns
        df[cat_cols] = df[cat_cols].astype("category")

        return df

    def predict_frequence(self, input_data: dict) -> float:
        """Prédit la fréquence de sinistres — résultat clampé entre 0 et 1."""
        df = self._build_features(input_data)
        result = float(max(0.0, min(1.0, self.model.predict_frequence(df))))
        logger.info("Fréquence prédite : %.4f", result)
        return result

    def predict_gravite(self, input_data: dict) -> float:
        """Prédit la gravité (coût moyen) — résultat toujours positif."""
        df = self._build_features(input_data)
        result = float(max(0.0, self.model.predict_gravite(df)))
        logger.info("Gravité prédite : %.2f", result)
        return result

    def predict_prime(self, input_data: dict) -> dict:
        """
        Calcule la prime pure complète.

        Args:
            input_data: Dictionnaire des données brutes.

        Returns:
            Dictionnaire avec fréquence, gravité et prime pure.
        """
        logger.info("Nouvelle prédiction pour : %s", input_data.get("marque_vehicule", "?"))
        df = self._build_features(input_data)

        frequence = float(max(0.0, min(1.0, self.model.predict_frequence(df))))
        gravite = float(max(0.0, self.model.predict_gravite(df)))
        prime = frequence * gravite

        result = {
            "frequence_predite": round(frequence, 4),
            "cout_moyen_predit": round(gravite, 2),
            "prime_pure": round(prime, 2),
        }
        logger.info("Résultat : fréquence=%.4f, gravité=%.2f, prime=%.2f",
                    frequence, gravite, prime)
        return result
