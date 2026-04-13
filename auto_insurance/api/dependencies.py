"""
Gestion du chargement des modèles pour l'injection de dépendances FastAPI.
Les modèles sont chargés une seule fois au démarrage de l'application.
"""

from functools import lru_cache

from auto_insurance.src.pipeline import PredictionPipeline


@lru_cache(maxsize=1)
def get_pipeline() -> PredictionPipeline:
    """Retourne l'instance du pipeline (singleton chargé une seule fois)."""
    return PredictionPipeline()
