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

    def predict_frequence(self, df: pd.DataFrame) -> float:
        """
        Prédit la fréquence de sinistres.

        Args:
            df: DataFrame d'une ligne prêt pour la prédiction.

        Returns:
            Fréquence prédite (float).
        """
        return float(self.model_frequence.predict(df)[0])

    def predict_gravite(self, df: pd.DataFrame) -> float:
        """
        Prédit le coût moyen d'un sinistre.

        Args:
            df: DataFrame d'une ligne prêt pour la prédiction.

        Returns:
            Coût moyen prédit (float).
        """
        return float(self.model_gravite.predict(df)[0])

    def predict_prime(
        self,
        df: pd.DataFrame,
        duree_contrat: float
    ) -> dict:
        """
        Calcule la prime pure complète.
        Formule : fréquence × coût moyen × durée contrat.

        Args:
            df: DataFrame d'une ligne prêt pour la prédiction.
            duree_contrat: Durée du contrat en années.

        Returns:
            Dictionnaire avec fréquence, gravité et prime pure.
        """
        frequence = self.predict_frequence(df)
        gravite = self.predict_gravite(df)
        prime = frequence * gravite * duree_contrat

        return {
            "frequence_predite": frequence,
            "cout_moyen_predit": gravite,
            "prime_pure": prime
        }