"""
Schémas Pydantic pour l'API d'assurance auto.
Définit les modèles d'entrée (contrat) et de sortie (prédictions).
"""

from pydantic import BaseModel, Field, model_validator


class InsuranceInput(BaseModel):
    """
    Données brutes d'un contrat d'assurance auto.
    Correspond exactement aux features attendues par les modèles XGBoost.
    """

    # Contrat
    type_contrat: str = Field(..., description="Type de contrat")
    duree_contrat: float = Field(..., ge=0, description="Durée du contrat (mois)")
    anciennete_info: float = Field(..., ge=0, description="Ancienneté client (années)")
    freq_paiement: str = Field(..., description="Fréquence de paiement")
    utilisation: str = Field(..., description="Utilisation du véhicule")
    code_postal: str = Field(..., description="Code postal du conducteur")

    # Conducteur principal
    age_conducteur1: float = Field(..., ge=18, le=100, description="Âge du conducteur principal")
    sex_conducteur1: str = Field(..., description="Sexe du conducteur : M ou F")
    anciennete_permis1: float = Field(..., ge=0, description="Ancienneté du permis (années)")

    # Véhicule
    anciennete_vehicule: float = Field(..., ge=0, description="Ancienneté du véhicule (années)")
    cylindre_vehicule: float = Field(..., ge=0, description="Cylindrée du véhicule")
    din_vehicule: float = Field(..., ge=0, description="Puissance du véhicule (DIN)")
    essence_vehicule: str = Field(..., description="Type de carburant")
    marque_vehicule: str = Field(..., description="Marque du véhicule")
    modele_vehicule: str = Field(..., description="Modèle du véhicule")
    fin_vente_vehicule: float = Field(..., description="Année de fin de commercialisation")
    vitesse_vehicule: float = Field(..., ge=0, description="Vitesse max du véhicule (km/h)")
    type_vehicule: str = Field(..., description="Type de véhicule")
    prix_vehicule: float = Field(..., ge=0, description="Prix du véhicule (€)")
    poids_vehicule: float = Field(..., ge=0, description="Poids du véhicule (kg)")

    @model_validator(mode="after")
    def check_age_permis_coherence(self):
        """Vérifie que l'âge d'obtention du permis est réaliste."""
        age_obtention = self.age_conducteur1 - self.anciennete_permis1
        if age_obtention < 16:
            raise ValueError(
                f"Incohérence détectée : permis obtenu à {age_obtention:.0f} ans — impossible."
            )
        return self

    model_config = {
        "json_schema_extra": {
            "example": {
                "type_contrat": "A",
                "duree_contrat": 12.0,
                "anciennete_info": 5.0,
                "freq_paiement": "mensuel",
                "utilisation": "prive",
                "code_postal": "75001",
                "age_conducteur1": 35.0,
                "sex_conducteur1": "M",
                "anciennete_permis1": 12.0,
                "anciennete_vehicule": 3.0,
                "cylindre_vehicule": 1600.0,
                "din_vehicule": 90.0,
                "essence_vehicule": "essence",
                "marque_vehicule": "Peugeot",
                "modele_vehicule": "308",
                "fin_vente_vehicule": 2022.0,
                "vitesse_vehicule": 180.0,
                "type_vehicule": "berline",
                "prix_vehicule": 18000.0,
                "poids_vehicule": 1200.0,
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
    niveau_risque: str = Field(
        ...,
        description="Niveau de risque : faible, modéré, élevé, très élevé"
    )
    model_version: str = Field(default="v1.0", description="Version du modèle utilisé")


class HealthResponse(BaseModel):
    """Réponse du endpoint de santé."""
    status: str
    message: str
