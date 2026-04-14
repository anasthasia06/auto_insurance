"""Application entry point for the auto insurance FastAPI service."""

import logging
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from starlette.responses import Response

from auto_insurance.api.endpoints.health import router as health_router
from auto_insurance.api.endpoints.predict import router as predict_router
from auto_insurance.api.logging_utils import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AutoAssur — API de Tarification Automobile",
    description="API REST propulsée par deux modèles XGBoost pour calculer la prime pure en temps réel. Fréquence × Gravité = Prime.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(health_router)
app.include_router(predict_router)


@app.middleware("http")
async def add_request_context(request: Request, call_next) -> Response:
    """Attach a request id and log the request lifecycle."""
    request_id = request.headers.get("x-request-id", str(uuid4()))
    logger.info(
        "Request started id=%s method=%s path=%s",
        request_id,
        request.method,
        request.url.path,
    )
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "Request completed id=%s method=%s path=%s status=%s",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
    )
    return response


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def landing_page():
    return """
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AutoAssur API</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 0; padding: 2rem; background: #f7fafc; color: #1a202c; }
    .card { max-width: 760px; margin: 0 auto; background: white; padding: 2rem; border-radius: 16px; box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08); }
    h1 { margin-top: 0; color: #1d4ed8; }
    ul { line-height: 1.8; }
    a { color: #2563eb; text-decoration: none; }
    code { background: #eff6ff; padding: 0.15rem 0.35rem; border-radius: 6px; }
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
