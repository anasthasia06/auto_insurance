"""
Module de chargement et prédiction des modèles d'assurance auto.
Gère les modèles de fréquence, gravité et le calcul de la prime pure.
"""

import pandas as pd
from xgboost import XGBRegressor


class InsuranceModel:
    """
    Chargement et prédiction des modèles XGBoost d'assurance auto.

    Attributes:
        model_frequence: Modèle XGBoost de fréquence des sinistres.
        model_gravite: Modèle XGBoost de gravité (coût moyen).
    """

    def __init__(self) -> None:
        self.model_frequence: XGBRegressor = XGBRegressor()
        self.model_gravite: XGBRegressor = XGBRegressor()
        self.feature_names: list[str] | None = None

    def load_models(
        self,
        path_frequence: str,
        path_gravite: str
    ) -> None:
        """
        Charge les modèles XGBoost depuis des fichiers JSON.

        Args:
            path_frequence: Chemin vers le fichier JSON du modèle fréquence.
            path_gravite: Chemin vers le fichier JSON du modèle gravité.
        """
        self.model_frequence.load_model(path_frequence)
        self.model_gravite.load_model(path_gravite)
        # Extraire les noms de features attendus par le modèle de fréquence.
        # Ils serviront pour aligner les DataFrame d'entrée avant prédiction.
        try:
            booster = self.model_frequence.get_booster()
            feature_names_seq = booster.feature_names
            # booster.feature_names may be a Sequence[str] or None —
            # convert to list[str] to satisfy the declared type.
            if feature_names_seq is not None:
                self.feature_names = list(feature_names_seq)
            else:
                self.feature_names = None
        except (AttributeError, ValueError, RuntimeError):
            # Cas où le booster ou les feature names ne sont pas disponibles.
            self.feature_names = None

    def predict_frequence(self, df: pd.DataFrame) -> float:
    result = self.model_frequence.predict(df)
    return float(result.flatten()[0])

    def predict_gravite(self, df: pd.DataFrame) -> float:
    result = self.model_gravite.predict(df)
    return float(result.flatten()[0])
    def predict_prime(
        self,
        df: pd.DataFrame,
    ) -> dict:
        """
        Calcule la prime pure complète.
        Formule : fréquence × coût moyen

        Args:
            df: DataFrame d'une ligne prêt pour la prédiction.

        Returns:
            Dictionnaire avec fréquence, gravité et prime pure.
        """
        frequence = self.predict_frequence(df)
        gravite = self.predict_gravite(df)
        prime = frequence * gravite

        return {
            "frequence_predite": frequence,
            "cout_moyen_predit": gravite,
            "prime_pure": prime
        }

    def get_feature_names(self) -> list[str] | None:
        """Retourne la liste des features attendues par le modèle (ou None)."""
        return self.feature_names
