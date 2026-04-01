"""
Point d'entrée de l'API FastAPI pour l'assurance auto.
Lance avec : uvicorn auto_insurance.api.main:app --reload
"""

from fastapi import FastAPI

from auto_insurance.api.endpoints.health import router as health_router
from auto_insurance.api.endpoints.predict import router as predict_router

app = FastAPI(
    title="Auto Insurance Pricing API",
    description=(
        "API de tarification d'assurance auto. "
        "Calcule la prime pure via deux modèles XGBoost : "
        "fréquence (probabilité de sinistre) × gravité (coût moyen)."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(health_router)
app.include_router(predict_router)
