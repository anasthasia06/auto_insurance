"""
Schémas Pydantic pour l'API d'assurance auto.
Définit les modèles d'entrée (contrat) et de sortie (prédictions).
"""

from pydantic import BaseModel, Field


class InsuranceInput(BaseModel):
    """
    Données brutes d'un contrat d'assurance auto.
    Correspond aux colonnes du dataset original (hors colonnes ID et cibles).
    """

    # Conducteur principal
    age_conducteur1: float = Field(..., ge=18, le=100, description="Âge du conducteur principal")
    anciennete_permis1: float = Field(..., ge=0, description="Ancienneté du permis (années)")
    sex_conducteur1: str = Field(..., description="Sexe du conducteur : M ou F")

    # Conducteur secondaire
    conducteur2: str = Field(default="No", description="Conducteur secondaire : Yes ou No")

    # Contrat
    paiement: str = Field(default="No", description="Mode de paiement : Yes ou No")

    # Véhicule
    poids_vehicule: float = Field(..., ge=0, description="Poids du véhicule (kg)")
    din_vehicule: float = Field(..., ge=0, description="Puissance du véhicule (DIN)")
    prix_vehicule: float = Field(..., ge=0, description="Prix du véhicule (€)")
    debut_vente_vehicule: float = Field(..., description="Année de début de commercialisation")
    fin_vente_vehicule: float = Field(..., description="Année de fin de commercialisation")

    model_config = {
        "json_schema_extra": {
            "example": {
                "age_conducteur1": 35,
                "anciennete_permis1": 12,
                "sex_conducteur1": "M",
                "conducteur2": "No",
                "paiement": "Yes",
                "poids_vehicule": 1200.0,
                "din_vehicule": 90.0,
                "prix_vehicule": 18000.0,
                "debut_vente_vehicule": 2015,
                "fin_vente_vehicule": 2022,
            }
        }
    }


class FrequenceResponse(BaseModel):
    """Réponse du modèle de fréquence."""
    frequence_predite: float = Field(..., description="Probabilité de sinistre prédite")


class GraviteResponse(BaseModel):
    """Réponse du modèle de gravité."""
    cout_moyen_predit: float = Field(..., description="Coût moyen d'un sinistre prédit (€)")


class PrimeResponse(BaseModel):
    """Réponse complète : fréquence × gravité = prime pure."""
    frequence_predite: float = Field(..., description="Probabilité de sinistre prédite")
    cout_moyen_predit: float = Field(..., description="Coût moyen d'un sinistre prédit (€)")
    prime_pure: float = Field(..., description="Prime pure = fréquence × gravité (€)")


class HealthResponse(BaseModel):
    """Réponse du endpoint de santé."""
    status: str
    message: str
