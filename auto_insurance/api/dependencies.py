"""
Gestion du chargement des modèles pour l'injection de dépendances FastAPI.
Les modèles sont chargés une seule fois au démarrage de l'application.
"""

from auto_insurance.src.pipeline import PredictionPipeline

# Instance globale (chargée une fois)
_PIPELINE: PredictionPipeline | None = None


def get_pipeline() -> PredictionPipeline:
    """Retourne l'instance du pipeline (singleton)."""
    global _PIPELINE  # pylint: disable=global-statement
    if _PIPELINE is None:
        _PIPELINE = PredictionPipeline()
    return _PIPELINE
