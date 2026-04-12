"""
Point d'entrée de l'API FastAPI pour l'assurance auto.
Lance avec : uvicorn auto_insurance.api.main:app --reload
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from auto_insurance.api.endpoints.health import router as health_router
from auto_insurance.api.endpoints.predict import router as predict_router

app = FastAPI(
    title="AutoAssur — API de Tarification Automobile",
    description=(
        "API REST propulsée par deux modèles XGBoost "
        "pour calculer la prime pure en temps réel. "
        "Fréquence × Gravité = Prime."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(health_router)
app.include_router(predict_router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def landing_page() -> HTMLResponse:
    """Retourne la page d'accueil HTML de l'API."""
    return """
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>AutoAssur — API de Tarification</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f8faff; color: #111827; }
    .header { background: #f0f5ff; padding: 2rem; border-bottom: 1px solid #dde6f7; }
    .logo { display: flex; align-items: center; gap: 10px; margin-bottom: 1.5rem; }
    .logo-icon { width: 34px; height: 34px; background: #2563eb; border-radius: 8px; display: flex; align-items: center; justify-content: center; }
    .logo-name { color: #1e3a8a; font-size: 15px; font-weight: 500; }
    .badge { margin-left: auto; background: #dbeafe; color: #1d4ed8; font-family: monospace; font-size: 11px; padding: 3px 8px; border-radius: 4px; border: 1px solid #bfdbfe; }
    h1 { color: #1e3a8a; font-size: 26px; font-weight: 600; line-height: 1.3; margin-bottom: 0.5rem; }
    .subtitle { color: #4b6cb7; font-size: 13px; line-height: 1.7; max-width: 400px; margin: 0.75rem 0 1.5rem; }
    .btns { display: flex; gap: 8px; flex-wrap: wrap; }
    .btn-primary { background: #2563eb; color: white; text-decoration: none; font-size: 12px; padding: 8px 18px; border-radius: 6px; font-weight: 500; }
    .btn-secondary { background: white; color: #2563eb; text-decoration: none; font-size: 12px; padding: 8px 18px; border-radius: 6px; border: 1px solid #bfdbfe; font-weight: 500; }
    .section { padding: 1.5rem 2rem; background: white; border-bottom: 1px solid #e5e7eb; }
    .section-label { font-size: 11px; color: #9ca3af; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 1rem; }
    .endpoint { border: 1px solid #e5e7eb; border-radius: 8px; padding: 11px 14px; display: flex; align-items: center; gap: 12px; background: #fafafa; margin-bottom: 8px; }
    .endpoint.featured { border: 2px solid #2563eb; background: #eff6ff; }
    .badge-get { background: #dcfce7; color: #15803d; font-family: monospace; font-size: 10px; padding: 3px 8px; border-radius: 4px; font-weight: 600; }
    .badge-post { background: #dbeafe; color: #1d4ed8; font-family: monospace; font-size: 10px; padding: 3px 8px; border-radius: 4px; font-weight: 600; }
    code { font-size: 13px; font-family: monospace; }
    .endpoint-desc { margin-left: auto; font-size: 12px; color: #9ca3af; }
    .endpoint-desc.featured { color: #2563eb; font-weight: 500; }
    .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
    .stat { background: #f0f5ff; border-radius: 8px; padding: 1rem; text-align: center; }
    .stat-num { font-size: 24px; font-weight: 600; color: #1e3a8a; }
    .stat-label { font-size: 11px; color: #4b6cb7; margin-top: 4px; }
    .formula { background: #f0f5ff; border-radius: 8px; padding: 1.25rem; display: flex; align-items: center; justify-content: center; gap: 16px; flex-wrap: wrap; }
    .formula-item { text-align: center; }
    .formula-label { color: #4b6cb7; font-family: monospace; font-size: 11px; margin-bottom: 4px; }
    .formula-value { color: #1e3a8a; font-size: 20px; font-weight: 600; }
    .formula-op { color: #93c5fd; font-size: 22px; font-weight: 300; }
    .formula-result { background: #2563eb; border-radius: 8px; padding: 8px 16px; text-align: center; }
    .formula-result .formula-label { color: #bfdbfe; }
    .formula-result .formula-value { color: white; }
  </style>
</head>
<body>
  <div class="header">
    <div class="logo">
      <div class="logo-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
        </svg>
      </div>
      <span class="logo-name">AutoAssur</span>
      <span class="badge">v1.0 · stable</span>
    </div>
    <h1>API de Tarification<br>Automobile</h1>
    <p class="subtitle">Calculez la prime pure d'assurance en temps réel grâce à deux modèles XGBoost — fréquence et gravité des sinistres.</p>
    <div class="btns">
      <a href="/docs" class="btn-primary">Swagger UI</a>
      <a href="/redoc" class="btn-secondary">ReDoc</a>
    </div>
  </div>

  <div class="section">
    <p class="section-label">Endpoints</p>
    <div class="endpoint">
      <span class="badge-get">GET</span>
      <code>/health</code>
      <span class="endpoint-desc">Statut de l'API</span>
    </div>
    <div class="endpoint">
      <span class="badge-post">POST</span>
      <code>/predict/frequency</code>
      <span class="endpoint-desc">Probabilité sinistre</span>
    </div>
    <div class="endpoint">
      <span class="badge-post">POST</span>
      <code>/predict/severity</code>
      <span class="endpoint-desc">Coût moyen sinistre</span>
    </div>
    <div class="endpoint featured">
      <span class="badge-post">POST</span>
      <code>/predict/premium</code>
      <span class="endpoint-desc featured">Prime pure complète</span>
    </div>
  </div>

  <div class="section">
    <div class="stats">
      <div class="stat">
        <p class="stat-num">20</p>
        <p class="stat-label">tests passés</p>
      </div>
      <div class="stat">
        <p class="stat-num">2</p>
        <p class="stat-label">modèles XGBoost</p>
      </div>
      <div class="stat">
        <p class="stat-num">24</p>
        <p class="stat-label">features ML</p>
      </div>
    </div>
  </div>

  <div class="section">
    <p class="section-label">Formule de tarification</p>
    <div class="formula">
      <div class="formula-item">
        <p class="formula-label">fréquence</p>
        <p class="formula-value">0.12</p>
      </div>
      <span class="formula-op">×</span>
      <div class="formula-item">
        <p class="formula-label">gravité</p>
        <p class="formula-value">3 500 €</p>
      </div>
      <span class="formula-op">=</span>
      <div class="formula-result">
        <p class="formula-label">prime pure</p>
        <p class="formula-value">420 €</p>
      </div>
    </div>
  </div>
</body>
</html>
"""
