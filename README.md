# auto_insurance
# Auto Insurance — API de prédiction de prime

API de prédiction de prime pure pour l'assurance automobile,
basée sur deux modèles XGBoost (fréquence et gravité des sinistres).

## Installation

### Prérequis
- Python 3.10+
- uv

### Installer les dépendances
```bash
python -m uv sync
```

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
```
auto_insurance/
├── .github/workflows/    # CI/CD GitHub Actions
├── auto_insurance/
│   ├── src/
│   │   ├── preprocessing.py  # Nettoyage des données
│   │   ├── features.py       # Feature engineering
│   │   └── model.py          # Modèles XGBoost
│   ├── api/                  # Endpoints FastAPI
│   └── models/               # Modèles sauvegardés
├── tests/                    # Tests unitaires
├── pyproject.toml
└── uv.lock
```

## Endpoints API

| Route | Description |
|-------|-------------|
| `/health` | Etat de santé de l'API |
| `/predict_frequency` | Prédiction de la fréquence |
| `/predict_amount` | Prédiction du montant |
| `/predict` | Prédiction de la prime pure |