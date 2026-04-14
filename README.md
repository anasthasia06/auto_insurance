# auto_insurance

API de prediction de prime pure pour l'assurance automobile, basee sur deux
modeles XGBoost: frequence et gravite des sinistres.

## Prerequis

- Python 3.10+
- `uv`
- Docker (optionnel)

## Installation locale

```bash
python -m uv sync --dev
```

## Lancer l'API en local

```bash
python -m uv run uvicorn auto_insurance.api.main:app --reload
```

API disponible sur `http://127.0.0.1:8000`

## Tests et qualite

```bash
python -m uv run ruff check auto_insurance tests
python -m uv run pylint auto_insurance/src/ --disable=C0114,C0116
python -m uv run mypy auto_insurance/src/
python -m uv run --with httpx pytest tests -v
```

## Docker

### Build

```bash
docker build -t auto-insurance-api .
```

### Run local

```bash
docker run --rm -p 8000:8000 auto-insurance-api
```

## Deploy Render

Configuration recommandee:

- Runtime: `Docker`
- Branche de deploy: `main`
- Health check path: `/health`
- Port: variable `PORT` fournie par Render

Le fichier `render.yaml` fournit une configuration de base pour ce deploy.

## Bonus logs et database

Le projet inclut maintenant:

- des logs applicatifs centralises
- un `X-Request-ID` ajoute sur chaque reponse HTTP
- un audit SQLite optionnel des predictions reussies

Variables d'environnement utiles:

- `LOG_LEVEL`: niveau de logs, par exemple `INFO` ou `DEBUG`
- `PREDICTION_AUDIT_ENABLED`: active l'audit SQLite si valeur `true`
- `PREDICTION_AUDIT_DB_PATH`: chemin du fichier SQLite, par defaut `data/prediction_audit.db`

Endpoints bonus:

- `/health/audit`: etat du stockage d'audit

Exemple d'activation locale:

```bash
$env:PREDICTION_AUDIT_ENABLED="true"
$env:PREDICTION_AUDIT_DB_PATH="data/prediction_audit.db"
python -m uv run uvicorn auto_insurance.api.main:app --reload
```

### Deploiement automatique avec GitHub Actions

Le workflow [cd-render.yml](</c:/Users/CYTech Student/auto_insurance/.github/workflows/cd-render.yml:1>)
declenche un deploy Render:

- automatiquement apres une CI reussie sur `main`
- manuellement depuis l'onglet GitHub Actions

Secret GitHub requis:

- `RENDER_DEPLOY_HOOK_URL`: URL du deploy hook Render

Pour recuperer cette URL dans Render:

1. ouvrir le service web
2. aller dans `Settings`
3. ouvrir `Deploy Hook`
4. copier l'URL et l'ajouter dans `Settings > Secrets and variables > Actions`

## Strategie de branches

- `main`: branche stable, prete pour le deploy
- `dev`: branche d'integration
- branches feature: une branche par personne ou fonctionnalite, puis Pull Request vers `dev`

Workflow recommande:

1. creer une branche depuis `dev`
2. ouvrir une Pull Request vers `dev`
3. merger `dev` vers `main` pour une release ou un deploy

Configuration GitHub ajoutee dans le repo:

- [PULL_REQUEST_TEMPLATE.md](</c:/Users/CYTech Student/auto_insurance/.github/PULL_REQUEST_TEMPLATE.md:1>)
- [CODEOWNERS](</c:/Users/CYTech Student/auto_insurance/.github/CODEOWNERS:1>)
- [BRANCH_STRATEGY.md](</c:/Users/CYTech Student/auto_insurance/.github/BRANCH_STRATEGY.md:1>)

Reglage manuel recommande dans GitHub:

1. proteger `dev` et `main`
2. imposer la PR avant merge
3. imposer le check `CI pipeline`
4. reserver le deploy automatique a `main`

## CI GitHub Actions

Le workflow GitHub Actions:

- installe Python 3.10 et `uv`
- installe les dependances du projet
- lance `ruff`, `pylint`, `mypy`
- lance `pytest`
- verifie que l'image Docker se build correctement

Le CD vers Render est separe de la CI:

- CI sur `dev` et `main`
- deploy seulement depuis `main`

## Endpoints API

| Route | Description |
|-------|-------------|
| `/health` | Etat de sante de l'API |
| `/predict/frequency` | Prediction de la frequence |
| `/predict/severity` | Prediction du cout moyen |
| `/predict/premium` | Prediction de la prime pure |
