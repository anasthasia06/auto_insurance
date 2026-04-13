# Auto Insurance — API de Tarification Automobile

![CI](https://github.com/anasthasia06/auto_insurance/actions/workflows/ci.yml/badge.svg?branch=dev)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688)
![Tests](https://img.shields.io/badge/tests-45%20passed-brightgreen)
![XGBoost](https://img.shields.io/badge/model-XGBoost-orange)

API REST de tarification automobile en temps réel, propulsée par deux modèles XGBoost indépendants selon la formule actuarielle standard :

```
Prime Pure = Fréquence × Gravité
```

---

## Table des matières

- [Logique ML](#logique-ml)
- [Architecture](#architecture)
- [Installation](#installation)
- [Lancer l'API](#lancer-lapi)
- [Endpoints](#endpoints)
- [Feature Engineering](#feature-engineering)
- [Pipeline d'inférence](#pipeline-dinférence)
- [Validation des données](#validation-des-données)
- [Tests](#tests)
- [CI/CD](#cicd)
- [Docker](#docker)

---

## Logique ML

Le projet repose sur une approche actuarielle standard en assurance non-vie. Deux modèles XGBoost distincts sont entraînés séparément, puis combinés :

| Modèle | Cible | Sortie |
|--------|-------|--------|
| **Fréquence** | Probabilité qu'un sinistre survienne | Valeur entre 0 et 1 |
| **Gravité** | Coût moyen d'un sinistre si il survient | Montant en euros (≥ 0) |
| **Prime Pure** | Fréquence × Gravité | Montant en euros |

**Pourquoi deux modèles séparés ?**
La fréquence et la gravité suivent des distributions statistiques différentes. Les modéliser séparément permet d'utiliser les objectifs de perte adaptés à chacun, et d'interpréter indépendamment le risque de sinistre et son coût moyen.

**Exemple concret :**
```
Fréquence prédite : 0.0842  (8.42% de chance de sinistre)
Gravité prédite   : 1 243 €  (coût moyen si sinistre)
Prime pure        : 0.0842 × 1 243 = 104.70 €
```

---

## Architecture

```
auto_insurance/
├── .github/
│   └── workflows/
│       └── ci.yml              # CI/CD — lint + tests automatiques
├── auto_insurance/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── health.py       # GET /health, GET /health/models
│   │   │   └── predict.py      # POST /predict/* (4 endpoints)
│   │   ├── schemas/
│   │   │   └── insurance.py    # Schémas Pydantic — input/output typés
│   │   ├── dependencies.py     # Singleton lru_cache — chargement unique
│   │   └── main.py             # Application FastAPI + page d'accueil
│   ├── src/
│   │   ├── preprocessing.py    # Nettoyage des données brutes
│   │   ├── features.py         # Feature engineering — 5 features métier
│   │   ├── model.py            # Chargement et prédiction XGBoost
│   │   └── pipeline.py         # Orchestration complète : input → prédiction
│   └── models/
│       ├── model_frequence.json # Modèle XGBoost — fréquence
│       ├── model_gravite.json   # Modèle XGBoost — gravité
│       └── encoder.pkl          # CountEncoder fitté au training
├── tests/
│   ├── test_api.py             # 25 tests — endpoints FastAPI
│   ├── test_features.py        # 12 tests — feature engineering
│   └── test_preprocessing.py  # 8 tests  — preprocessing
├── Dockerfile
├── pyproject.toml
└── uv.lock
```

**Flux d'une requête :**
```
Client JSON
    ↓
FastAPI (main.py)
    ↓
Validation Pydantic (schemas/insurance.py)  ← erreur 422 si invalide
    ↓
Endpoint (endpoints/predict.py)
    ↓
PredictionPipeline (src/pipeline.py)
    ↓  ↓
DataPreprocessor  FeatureEngineer    ← preprocessing + features
    ↓
InsuranceModel (XGBoost × 2)        ← fréquence + gravité
    ↓
prime = fréquence × gravité
    ↓
Réponse JSON typée (Pydantic)
```

---

## Installation

### Prérequis

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (gestionnaire de dépendances)

### Installer les dépendances

```bash
uv sync
```

### Installer en mode développement

```bash
pip install -e ".[dev]"
```

---

## Lancer l'API

```bash
uvicorn auto_insurance.api.main:app --reload
```

| URL | Description |
|-----|-------------|
| http://localhost:8000 | Page d'accueil |
| http://localhost:8000/docs | Documentation Swagger interactive |
| http://localhost:8000/redoc | Documentation ReDoc |

---

## Endpoints

### GET `/health`

Vérifie que l'API est opérationnelle.

```bash
curl http://localhost:8000/health
```

```json
{
  "status": "ok",
  "message": "API opérationnelle"
}
```

---

### GET `/health/models`

Vérifie que les deux modèles XGBoost sont chargés en mémoire.

```json
{
  "status": "ok",
  "models": {
    "frequence": { "loaded": true, "features": 24, "version": "v1.0" },
    "gravite":   { "loaded": true, "features": 24, "version": "v1.0" }
  }
}
```

---

### POST `/predict/frequency`

Prédit la probabilité qu'un sinistre survienne.

**Input :** `InsuranceInput` (voir [Validation des données](#validation-des-données))

**Output :**
```json
{
  "frequence_predite": 0.0842
}
```

---

### POST `/predict/severity`

Prédit le coût moyen d'un sinistre si il survient.

**Output :**
```json
{
  "cout_moyen_predit": 1243.50
}
```

---

### POST `/predict/premium`

Calcule la prime pure complète : `fréquence × gravité`.

**Output :**
```json
{
  "frequence_predite": 0.0842,
  "cout_moyen_predit": 1243.50,
  "prime_pure": 104.70,
  "niveau_risque": "modéré",
  "model_version": "v1.0"
}
```

Niveaux de risque : `faible` (< 5%) · `modéré` (5–10%) · `élevé` (10–20%) · `très élevé` (> 20%)

---

### POST `/predict/explain`

Calcule la prime pure et liste les facteurs de risque détectés.

**Output :**
```json
{
  "frequence_predite": 0.0842,
  "cout_moyen_predit": 1243.50,
  "prime_pure": 104.70,
  "niveau_risque": "modéré",
  "facteurs_de_risque": [
    "Permis récent — manque d'expérience"
  ],
  "model_version": "v1.0"
}
```

---

### Exemple de requête complète

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

---

## Feature Engineering

Les features brutes du contrat sont enrichies par 5 variables métier calculées dans `src/features.py` :

| Feature | Formule | Justification métier |
|---------|---------|----------------------|
| `ratio_poids_puissance` | `poids / (puissance + ε)` | Un véhicule puissant et léger est plus nerveux et plus risqué |
| `age_obtention_permis` | `âge - ancienneté permis` | Isole l'expérience réelle de conduite indépendamment de l'âge |
| `jeune_conducteur` | `1 si ancienneté permis < 3 ans` | Flag binaire — les conducteurs novices ont un sur-risque statistique documenté |
| `duree_vie_modele` | `fin_vente - debut_vente` | Proxy de popularité et fiabilité du modèle de véhicule |
| `log_prix_vehicule` | `log(1 + prix)` | Normalise la distribution très asymétrique des prix de véhicules |

**Total : 24 features** envoyées aux modèles XGBoost (20 brutes + 4 dérivées, `jeune_conducteur` n'étant pas dans `EXPECTED_COLS`).

---

## Pipeline d'inférence

Le pipeline dans `src/pipeline.py` orchestre toutes les étapes d'une prédiction :

```python
class PredictionPipeline:
    def _build_features(self, input_data: dict) -> pd.DataFrame:
        # 1. Gérer le champ optionnel debut_vente_vehicule
        # 2. DataPreprocessor.transform() — nettoyage + CountEncoder
        # 3. FeatureEngineer.transform()  — 5 features dérivées
        # 4. Alignement strict sur les 24 colonnes EXPECTED_COLS
        # 5. Conversion en type "category" pour XGBoost natif
```

**Garantie train = inference :**
- Le `CountEncoder` est fitté **une seule fois** au training et sauvegardé dans `encoder.pkl`
- En inférence, il est chargé tel quel — jamais refitté
- `EXPECTED_COLS` garantit l'ordre exact des 24 colonnes attendues par XGBoost

**Chargement unique des modèles** via `@lru_cache(maxsize=1)` dans `dependencies.py` :
```python
@lru_cache(maxsize=1)
def get_pipeline() -> PredictionPipeline:
    return PredictionPipeline()
```
Les modèles sont chargés une seule fois au démarrage et réutilisés pour toutes les requêtes.

---

## Validation des données

Toutes les données entrantes sont validées par Pydantic (`schemas/insurance.py`) avant d'atteindre le modèle ML.

### Contraintes sur les champs

| Champ | Type | Contraintes |
|-------|------|-------------|
| `age_conducteur1` | float | ≥ 18, ≤ 100 |
| `anciennete_permis1` | float | ≥ 0 |
| `din_vehicule` | float | ≥ 0 |
| `prix_vehicule` | float | ≥ 0 |
| `poids_vehicule` | float | ≥ 0 |
| `debut_vente_vehicule` | float ou absent | Optionnel — fallback : fin_vente - 5 ans |

### Validation métier croisée

```python
@model_validator(mode="after")
def check_age_permis_coherence(self):
    age_obtention = self.age_conducteur1 - self.anciennete_permis1
    if age_obtention < 16:
        raise ValueError("Permis impossible — obtenu trop jeune")
```

Si les données sont invalides, l'API retourne automatiquement une erreur **422 Unprocessable Entity** avec le détail de l'erreur — sans jamais appeler le modèle ML.

---

## Tests

```bash
python -m pytest tests/ -v
```

**45 tests — 45 passés**

| Fichier | Tests | Ce qui est couvert |
|---------|-------|--------------------|
| `test_api.py` | 25 | Endpoints HTTP, validation Pydantic, cas d'erreur, formule prime |
| `test_features.py` | 12 | Chaque feature dérivée — valeur exacte + non-modification du DataFrame original |
| `test_preprocessing.py` | 8 | Nettoyage, encodage binaire, absence de NaN après transform |

**Types de tests :**

```python
# Cas normal (happy path)
def test_premium_status_200(self):
    response = client.post("/predict/premium", json=VALID_PAYLOAD)
    assert response.status_code == 200

# Validation Pydantic — champ manquant
def test_frequency_missing_field(self):
    payload = VALID_PAYLOAD.copy()
    del payload["age_conducteur1"]
    assert client.post("/predict/frequency", json=payload).status_code == 422

# Validation métier croisée
def test_impossible_age_permis(self):
    payload = {**VALID_PAYLOAD, "age_conducteur1": 20, "anciennete_permis1": 15}
    assert client.post("/predict/premium", json=payload).status_code == 422

# Cohérence de la formule ML
def test_premium_formula(self):
    body = client.post("/predict/premium", json=VALID_PAYLOAD).json()
    assert abs(body["prime_pure"] - body["frequence_predite"] * body["cout_moyen_predit"]) < 1.0
```

---

## Lancer le lint

```bash
python -m ruff check auto_insurance/
python -m pylint auto_insurance/src/
python -m mypy auto_insurance/src/
```

---

## CI/CD

Le pipeline GitHub Actions se déclenche automatiquement à chaque push sur `dev` et `main` :

```
push → lint (ruff + pylint + mypy) → tests (45 tests pytest)
```

Configuration : `.github/workflows/ci.yml`

---

## Docker

### Build

```bash
docker build -t auto_insurance .
```

### Run

```bash
docker run -p 8000:8000 auto_insurance
```

L'API est disponible sur http://localhost:8000