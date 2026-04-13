# auto_insurance
# Auto Insurance — API de prédiction de prime pure

API de prédiction de prime pure pour l'assurance automobile,
basée sur deux modèles XGBoost (fréquence et gravité des sinistres).

> **Formule** : Prime Pure = Fréquence × Gravité

## Installation

### Prérequis
- Python 3.10+
- [uv](https://docs.astral.sh/uv/)

### Installer les dépendances
```bash
uv sync
```

### Installer en mode développement (avec outils de test et lint)
```bash
pip install -e ".[dev]"
```

## Lancer l'API
```bash
uvicorn auto_insurance.api.main:app --reload
```

L'API est disponible sur http://localhost:8000  
La documentation Swagger est sur http://localhost:8000/docs

## Lancer les tests
```bash
python -m pytest tests/ -v
```

## Lancer le lint
```bash
python -m ruff check auto_insurance/
python -m pylint auto_insurance/src/
python -m mypy auto_insurance/src/
```

## Structure du projet
auto_insurance/
├── .github/
│   └── workflows/
│       └── ci.yml              # CI/CD GitHub Actions
├── auto_insurance/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── health.py       # Endpoints de santé
│   │   │   └── predict.py      # Endpoints de prédiction
│   │   ├── schemas/
│   │   │   └── insurance.py    # Schémas Pydantic (input/output)
│   │   ├── dependencies.py     # Singleton pipeline (chargement modèles)
│   │   └── main.py             # Application FastAPI
│   ├── src/
│   │   ├── preprocessing.py    # Nettoyage des données
│   │   ├── features.py         # Feature engineering
│   │   ├── model.py            # Modèles XGBoost
│   │   └── pipeline.py         # Pipeline d'inférence complet
│   └── models/
│       ├── model_frequence.json
│       ├── model_gravite.json
│       └── encoder.pkl
├── tests/
│   ├── test_api.py             # Tests des endpoints FastAPI
│   ├── test_features.py        # Tests du feature engineering
│   └── test_preprocessing.py  # Tests du preprocessing
├── Dockerfile
├── pyproject.toml
└── uv.lock

## Endpoints API

| Route | Méthode | Description |
|-------|---------|-------------|
| `/` | GET | Page d'accueil |
| `/health` | GET | État de santé de l'API |
| `/health/models` | GET | État de chargement des modèles |
| `/predict/frequency` | POST | Probabilité de sinistre (fréquence) |
| `/predict/severity` | POST | Coût moyen d'un sinistre (gravité) |
| `/predict/premium` | POST | Prime pure = fréquence × gravité |
| `/predict/explain` | POST | Prime pure + facteurs de risque explicatifs |

## Exemple de requête
```bash
curl -X POST "http://localhost:8000/predict/premium" \
  -H "Content-Type: application/json" \
  -d '{
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
    "poids_vehicule": 1200.0
  }'
```

### Réponse attendue
```json
{
  "frequence_predite": 0.0842,
  "cout_moyen_predit": 1243.50,
  "prime_pure": 104.70,
  "niveau_risque": "modéré",
  "model_version": "v1.0"
}
```

## CI/CD

Le pipeline GitHub Actions tourne automatiquement à chaque push sur `dev` et `main` :
- Lint : `ruff`, `pylint`, `mypy`
- Tests : `pytest` (45 tests)

## Docker
```bash
docker build -t auto_insurance .
docker run -p 8000:8000 auto_insurance
```