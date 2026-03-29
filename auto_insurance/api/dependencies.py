"""
Gestion du chargement des modèles pour l'injection de dépendances FastAPI.
Les modèles sont chargés une seule fois au démarrage de l'application.
"""

from pathlib import Path

from auto_insurance.src.model import InsuranceModel
from auto_insurance.src.preprocessing import DataPreprocessor
from auto_insurance.src.features import FeatureEngineer

# Chemins vers les fichiers de modèles
MODELS_DIR = Path(__file__).parent.parent / "models"
PATH_FREQUENCE = MODELS_DIR / "model_frequence.json"
PATH_GRAVITE = MODELS_DIR / "model_gravite.json"
PATH_ENCODER = MODELS_DIR / "encoder.pkl"

# Instances globales (chargées une fois)
_model: InsuranceModel | None = None
_preprocessor: DataPreprocessor | None = None
_feature_engineer: FeatureEngineer | None = None


def get_model() -> InsuranceModel:
    """Retourne l'instance du modèle (singleton)."""
    global _model
    if _model is None:
        _model = InsuranceModel()
        _model.load_models(str(PATH_FREQUENCE), str(PATH_GRAVITE))
    return _model


def get_preprocessor() -> DataPreprocessor:
    """Retourne le préprocesseur avec l'encoder chargé (singleton)."""
    global _preprocessor
    if _preprocessor is None:
        _preprocessor = DataPreprocessor()
        _preprocessor.load_encoder(str(PATH_ENCODER))
    return _preprocessor


def get_feature_engineer() -> FeatureEngineer:
    """Retourne le feature engineer (singleton, stateless)."""
    global _feature_engineer
    if _feature_engineer is None:
        _feature_engineer = FeatureEngineer()
    return _feature_engineer
