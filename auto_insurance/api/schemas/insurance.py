"""
Pydantic schemas for the AutoAssur motor insurance pricing API.

Defines input (InsuranceInput) and output schemas
(FrequenceResponse, GraviteResponse, PrimeResponse, ExplainResponse).

The model version is stored in the MODEL_VERSION constant defined here
and imported by all endpoints. This avoids having "v1.0" hardcoded
in multiple places — update it here only when the model changes.
"""

from pydantic import BaseModel, Field, model_validator, field_validator

# ── Centralised model version ────────────────────────────────────────────────
# Update this constant only when deploying a new model version.
# Imported by predict.py to populate the model_version field in all responses.
MODEL_VERSION = "v1.0"


# ── Input schema ─────────────────────────────────────────────────────────────

class InsuranceInput(BaseModel):

    # ── Contract ──────────────────────────────────────────────────────────────
    type_contrat: str = Field(...)
    duree_contrat: float = Field(..., ge=0)
    anciennete_info: float = Field(..., ge=0)
    freq_paiement: str = Field(...)
    utilisation: str = Field(...)
    code_postal: str = Field(...)

    # ── Main driver ───────────────────────────────────────────────────────────
    age_conducteur1: float = Field(..., ge=18, le=100)
    sex_conducteur1: str = Field(...)
    anciennete_permis1: float = Field(..., ge=0)

    # ── Vehicle ───────────────────────────────────────────────────────────────
    anciennete_vehicule: float = Field(..., ge=0)
    cylindre_vehicule: float = Field(..., ge=0)
    din_vehicule: float = Field(..., ge=0)
    essence_vehicule: str = Field(...)
    marque_vehicule: str = Field(...)
    modele_vehicule: str = Field(...)
    fin_vente_vehicule: float = Field(...)
    debut_vente_vehicule: float | None = Field(default=None)
    vitesse_vehicule: float = Field(..., ge=0)
    type_vehicule: str = Field(...)
    prix_vehicule: float = Field(..., ge=0)
    poids_vehicule: float = Field(..., ge=0)

    conducteur2: str | None = Field(default=None)

    @field_validator(
        "duree_contrat",
        "anciennete_info",
        "age_conducteur1",
        "anciennete_permis1",
        "anciennete_vehicule",
        "cylindre_vehicule",
        "din_vehicule",
        "fin_vente_vehicule",
        "debut_vente_vehicule",
        "vitesse_vehicule",
        "prix_vehicule",
        "poids_vehicule",
        mode="before"
    )
    def fix_numeric_types(cls, v):
        if isinstance(v, list):
            v = v[0]
        if v == "":
            return None
        try:
            return float(v)
        except Exception:
            return v

    # ── Business validation ───────────────────────────────────────────────────
    @model_validator(mode="after")
    def check_licence_age_coherence(self):
        licence_age = self.age_conducteur1 - self.anciennete_permis1
        if licence_age < 16:
            raise ValueError("Licence incohérente")
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
# ── Output schemas ────────────────────────────────────────────────────────────

class FrequenceResponse(BaseModel):
    """Response schema for the frequency model."""
    frequence_predite: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Predicted claim probability, clamped between 0 and 1",
    )


class GraviteResponse(BaseModel):
    """Response schema for the severity model."""
    cout_moyen_predit: float = Field(
        ...,
        ge=0.0,
        description="Predicted average claim cost (€)",
    )


class PrimeResponse(BaseModel):
    """
    Full response: pure premium = frequency x severity.

    The model_version field is populated from the MODEL_VERSION constant.
    It must never be hardcoded directly in endpoint handlers.
    """
    frequence_predite: float = Field(
        ..., description="Predicted claim probability"
    )
    cout_moyen_predit: float = Field(
        ..., description="Predicted average claim cost (€)"
    )
    prime_pure: float = Field(
        ..., description="Pure premium = frequency x severity (€)"
    )
    niveau_risque: str = Field(
        ...,
        description="Risk level: faible | modéré | élevé | très élevé",
    )
    model_version: str = Field(
        default=MODEL_VERSION,
        description="Version of the XGBoost models used",
    )


class ExplainResponse(BaseModel):
    """
    Enriched response: pure premium + top risk factors (SHAP).

    Addresses the GDPR Article 22 requirement for explainability
    in automated decision-making systems.
    """
    frequence_predite: float = Field(
        ..., description="Predicted claim probability"
    )
    cout_moyen_predit: float = Field(
        ..., description="Predicted average claim cost (€)"
    )
    prime_pure: float = Field(
        ..., description="Pure premium = frequency x severity (€)"
    )
    niveau_risque: str = Field(
        ..., description="Risk level: faible | modéré | élevé | très élevé"
    )
    facteurs_de_risque: list[str] = Field(
        ...,
        description=(
            "Top 3 most influential risk factors, "
            "computed via SHAP TreeExplainer on the frequency model"
        ),
    )
    model_version: str = Field(
        default=MODEL_VERSION,
        description="Version of the XGBoost models used",
    )


class HealthResponse(BaseModel):
    """Response schema for the health check endpoint."""
    status: str = Field(..., description="API status (ok | degraded | down)")
    message: str = Field(..., description="Descriptive status message")
