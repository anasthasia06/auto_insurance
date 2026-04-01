"""
Gestion du chargement des modèles pour l'injection de dépendances FastAPI.
Les modèles sont chargés une seule fois au démarrage de l'application.
"""

from auto_insurance.src.pipeline import PredictionPipeline

# Instance globale (chargée une fois)
_pipeline: PredictionPipeline | None = None


def get_pipeline() -> PredictionPipeline:
    """Retourne l'instance du pipeline (singleton)."""
    global _pipeline
    if _pipeline is None:
        _pipeline = PredictionPipeline()
    return _pipeline