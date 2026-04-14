# AutoAssur — API de Tarification Automobile

API REST de calcul de prime pure pour l'assurance automobile,
basée sur deux modèles XGBoost (fréquence et gravité des sinistres).

**Formule actuarielle** : `Prime Pure = Fréquence × Gravité`

🚀 **Demo en ligne** : [Swagger UI (Render)](https://api-auto-insurance-wissal.onrender.com/docs)

---

## Endpoints

| Méthode | Route | Description |
|---------|-------|-------------|
| `GET` | `/health` | Statut de l'API |
| `GET` | `/health/models` | Statut de chargement des modèles XGBoost |
| `POST` | `/predict/frequency` | Probabilité de sinistre (fréquence) |
| `POST` | `/predict/severity` | Coût moyen d'un sinistre (gravité) |
| `POST` | `/predict/premium` | Prime pure complète = fréquence × gravité |
| `POST` | `/predict/explain` | Prime pure + facteurs de risque (SHAP) |

---

## Installation

### Prérequis
- Python 3.10+
- pip

### Installer le projet (mode développement)

```bash
pip install -e ".[dev]"
```

### Lancer l'API

```bash
uvicorn auto_insurance.api.main:app --reload
```

L'API est accessible sur `http://localhost:8000`.
La documentation Swagger est disponible sur `http://localhost:8000/docs`.

### Variables d'environnement

| Variable | Valeur par défaut | Description |
|----------|-------------------|-------------|
| `LOG_LEVEL` | `INFO` | Niveau de log (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

---

## Lancer les tests

```bash
pytest tests/ -v
```

45 tests couvrant :
- les endpoints API (`tests/test_api.py`)
- le feature engineering (`tests/test_features.py`)
- le preprocessing (`tests/test_preprocessing.py`)

---

## Lancer le lint et le typage

```bash
ruff check auto_insurance/
pylint auto_insurance/src/
mypy auto_insurance/src/
```

---

## Docker

### Construire l'image

```bash
docker build -t auto-insurance .
```

### Lancer le container

```bash
docker run -p 8000:8000 auto-insurance
```

---

## Structure du projet

```
auto_insurance/
├── .github/
│   └── workflows/
│       └── ci.yml              # CI/CD GitHub Actions (tests + lint)
├── auto_insurance/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── health.py       # GET /health, GET /health/models
│   │   │   └── predict.py      # POST /predict/frequency|severity|premium|explain
│   │   ├── schemas/
│   │   │   └── insurance.py    # Schémas Pydantic (input + output)
│   │   ├── dependencies.py     # Singleton pipeline (lru_cache)
│   │   ├── logging_config.py   # Logging structuré JSON
│   │   └── main.py             # FastAPI app + middleware de logging
│   ├── models/
│   │   ├── model_frequence.json  # Modèle XGBoost fréquence
│   │   ├── model_gravite.json    # Modèle XGBoost gravité
│   │   └── encoder.pkl           # CountEncoder (variables catégorielles)
│   └── src/
│       ├── features.py         # Feature engineering (5 features métier)
│       ├── model.py            # Chargement et prédiction XGBoost
│       ├── pipeline.py         # Orchestration preprocessing → features → modèle
│       └── preprocessing.py    # Nettoyage, encodage, CountEncoder
├── tests/
│   ├── test_api.py             # Tests endpoints FastAPI (25 tests)
│   ├── test_features.py        # Tests unitaires FeatureEngineer (12 tests)
│   └── test_preprocessing.py   # Tests unitaires DataPreprocessor (8 tests)
├── Dockerfile
├── pyproject.toml
└── README.md
```

---

## Exemple de requête

```bash
curl -X POST http://localhost:8000/predict/premium \
  -H "Content-Type: application/json" \
  -d '{
    "type_contrat": "A",
    "duree_contrat": 12,
    "anciennete_info": 5,
    "freq_paiement": "mensuel",
    "utilisation": "prive",
    "code_postal": "75001",
    "age_conducteur1": 35,
    "sex_conducteur1": "M",
    "anciennete_permis1": 12,
    "anciennete_vehicule": 3,
    "cylindre_vehicule": 1600,
    "din_vehicule": 90,
    "essence_vehicule": "essence",
    "marque_vehicule": "Peugeot",
    "modele_vehicule": "308",
    "fin_vente_vehicule": 2022,
    "vitesse_vehicule": 180,
    "type_vehicule": "berline",
    "prix_vehicule": 18000,
    "poids_vehicule": 1200
  }'
```

Réponse :

```json
{
  "frequence_predite": 0.0842,
  "cout_moyen_predit": 3241.50,
  "prime_pure": 272.93,
  "niveau_risque": "modéré",
  "model_version": "v1.0"
}
```

---

## Logging

Les logs sont produits en **format JSON structuré**, lisibles par des outils
de monitoring (ELK, Datadog, CloudWatch) :

```json
{
  "timestamp": "2024-01-15T10:23:45.123Z",
  "level": "INFO",
  "logger": "auto_insurance.api.endpoints.predict",
  "message": "Prime pure calculée avec succès",
  "endpoint": "/predict/premium",
  "latency_ms": 42.7,
  "marque_vehicule": "Peugeot",
  "model_version": "v1.0"
}
```

---

## Stack technique

| Composant | Technologie |
|-----------|-------------|
| API | FastAPI + Pydantic v2 |
| Modèles ML | XGBoost (fréquence + gravité) |
| Preprocessing | CountEncoder (category_encoders) |
| Explicabilité | SHAP TreeExplainer |
| Tests | pytest (45 tests) |
| Lint / typage | ruff, pylint, mypy |
| CI/CD | GitHub Actions |
| Déploiement | Docker + Render |
